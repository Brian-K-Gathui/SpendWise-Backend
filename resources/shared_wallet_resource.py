from flask_restful import Resource, reqparse
from flask import g, request
from models import db, SharedWallet, User, Wallet, Notification
from services.supabase_service import SupabaseService
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

logger = logging.getLogger(__name__)

class SharedWalletResource(Resource):
    def __init__(self):
        self.supabase_service = SupabaseService()

    def get(self, shared_wallet_id=None):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # If shared_wallet_id is provided, get that specific shared wallet
            if shared_wallet_id:
                shared_wallet = SharedWallet.query.filter_by(id=shared_wallet_id).first()
                if not shared_wallet:
                    return {"error": "Shared wallet not found"}, 404

                # Check if user has access to this shared wallet
                if shared_wallet.owner_id != user_id and shared_wallet.member_id != user_id:
                    return {"error": "Access denied"}, 403

                return shared_wallet.to_dict()

            # Otherwise, return all shared wallets for the user (both owned and shared with)
            owned_wallets = SharedWallet.query.filter_by(owner_id=user_id).all()
            shared_with_me = SharedWallet.query.filter_by(member_id=user_id).all()

            return {
                "owned": [wallet.to_dict() for wallet in owned_wallets],
                "shared_with_me": [wallet.to_dict() for wallet in shared_with_me]
            }

        except OperationalError as e:
            logger.error(f"Database connection error in GET /shared-wallets: {str(e)}")
            db.session.rollback()
            return {"error": "Database connection error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error in GET /shared-wallets: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def post(self):
        try:
            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('wallet_id', type=int, required=True, help='Wallet ID is required')
            parser.add_argument('member_email', type=str, required=True, help='Member email is required')
            parser.add_argument('permission', type=str, required=False, default='viewer')
            args = parser.parse_args()

            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            # Check if wallet exists and belongs to user
            wallet = Wallet.query.filter_by(id=args['wallet_id'], user_id=user_id).first()
            if not wallet:
                return {"error": "Wallet not found or access denied"}, 404

            # Find the member by email
            member = User.query.filter_by(email=args['member_email']).first()
            if not member:
                return {"error": "Member not found. They need to register first."}, 404

            # Check if sharing already exists
            existing_share = SharedWallet.query.filter_by(
                wallet_id=args['wallet_id'],
                owner_id=user_id,
                member_id=member.id
            ).first()

            if existing_share:
                return {"error": "Wallet is already shared with this user"}, 409

            # Create new shared wallet
            new_shared_wallet = SharedWallet(
                wallet_id=args['wallet_id'],
                owner_id=user_id,
                member_id=member.id,
                permission=args['permission']
            )

            # Create notification for the member
            notification = Notification(
                user_id=member.id,
                title="Wallet Shared With You",
                message=f"{user.full_name or user.email} has shared their wallet '{wallet.name}' with you.",
                type="shared_wallet_invite"
            )

            try:
                db.session.add(new_shared_wallet)
                db.session.add(notification)
                db.session.commit()
                return {
                    "message": "Wallet shared successfully",
                    "shared_wallet": new_shared_wallet.to_dict()
                }, 201
            except Exception as e:
                logger.error(f"Error sharing wallet: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in POST /shared-wallets: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, shared_wallet_id):
        try:
            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('permission', type=str, required=True, help='Permission is required')
            args = parser.parse_args()

            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the shared wallet
            shared_wallet = SharedWallet.query.get(shared_wallet_id)
            if not shared_wallet:
                return {"error": "Shared wallet not found"}, 404

            # Check if user is the owner
            if shared_wallet.owner_id != user_id:
                return {"error": "Only the owner can update permissions"}, 403

            # Update permission
            shared_wallet.permission = args['permission']

            try:
                db.session.commit()
                return {
                    "message": "Permission updated successfully",
                    "shared_wallet": shared_wallet.to_dict()
                }
            except Exception as e:
                logger.error(f"Error updating permission: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in PUT /shared-wallets/{shared_wallet_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, shared_wallet_id):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the shared wallet
            shared_wallet = SharedWallet.query.get(shared_wallet_id)
            if not shared_wallet:
                return {"error": "Shared wallet not found"}, 404

            # Check if user is the owner or the member
            if shared_wallet.owner_id != user_id and shared_wallet.member_id != user_id:
                return {"error": "Access denied"}, 403

            try:
                db.session.delete(shared_wallet)

                # Create notification for the other party
                if shared_wallet.owner_id == user_id:
                    # Notify the member
                    notification = Notification(
                        user_id=shared_wallet.member_id,
                        title="Wallet Access Removed",
                        message=f"Your access to the wallet '{shared_wallet.wallet.name}' has been removed.",
                        type="shared_wallet_update"
                    )
                else:
                    # Notify the owner
                    notification = Notification(
                        user_id=shared_wallet.owner_id,
                        title="Wallet Sharing Declined",
                        message=f"A user has removed themselves from your shared wallet '{shared_wallet.wallet.name}'.",
                        type="shared_wallet_update"
                    )

                db.session.add(notification)
                db.session.commit()

                return {
                    "message": "Shared wallet access removed successfully"
                }
            except Exception as e:
                logger.error(f"Error removing shared wallet: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in DELETE /shared-wallets/{shared_wallet_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500
