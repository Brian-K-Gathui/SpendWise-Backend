from flask_restful import Resource, reqparse
from flask import g, request
from models import db, Wallet, User
from services.supabase_service import SupabaseService
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

logger = logging.getLogger(__name__)

class WalletResource(Resource):
    def __init__(self):
        self.supabase_service = SupabaseService()

    def get(self, wallet_id=None):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # If wallet_id is provided, get that specific wallet
            if wallet_id:
                wallet = Wallet.query.filter_by(id=wallet_id, user_id=user_id).first()
                if not wallet:
                    return {"error": "Wallet not found or access denied"}, 404

                return wallet.to_dict()

            # Otherwise, return all wallets for the user
            wallets = Wallet.query.filter_by(user_id=user_id).all()
            return [wallet.to_dict() for wallet in wallets]

        except OperationalError as e:
            logger.error(f"Database connection error in GET /wallets: {str(e)}")
            db.session.rollback()
            return {"error": "Database connection error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error in GET /wallets: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def post(self):
        try:
            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=True, help='Wallet name is required')
            parser.add_argument('description', type=str, required=False)
            parser.add_argument('balance', type=float, required=False, default=0.0)
            parser.add_argument('currency', type=str, required=False, default='KES')
            parser.add_argument('type', type=str, required=False, default='personal')
            args = parser.parse_args()

            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Check if user exists in local database
            user = User.query.get(user_id)

            # If not in local database, check Supabase
            if not user:
                supabase_user = self.supabase_service.get_user_data(user_id)
                if not supabase_user:
                    # If user doesn't exist in Supabase either, create them
                    email = g.user.get('email', '')
                    self.supabase_service.create_or_update_user(user_id, email, {})

                    # Also create in local database
                    user = User(
                        id=user_id,
                        email=email
                    )
                    db.session.add(user)
                    db.session.commit()
                else:
                    # Create user in local database from Supabase data
                    user = User(
                        id=user_id,
                        email=supabase_user.get('email', '')
                    )
                    db.session.add(user)
                    db.session.commit()

            # Create new wallet
            new_wallet = Wallet(
                user_id=user_id,
                name=args['name'],
                description=args.get('description', ''),
                balance=args.get('balance', 0.0),
                currency=args.get('currency', 'KES'),
                type=args.get('type', 'personal')
            )

            try:
                db.session.add(new_wallet)
                db.session.commit()
                return {
                    "message": "Wallet created successfully",
                    "wallet": new_wallet.to_dict()
                }, 201
            except Exception as e:
                logger.error(f"Error creating wallet: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in POST /wallets: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, wallet_id):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the wallet
            wallet = Wallet.query.filter_by(id=wallet_id, user_id=user_id).first()
            if not wallet:
                return {"error": "Wallet not found or access denied"}, 404

            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=False)
            parser.add_argument('description', type=str, required=False)
            parser.add_argument('balance', type=float, required=False)
            parser.add_argument('currency', type=str, required=False)
            parser.add_argument('type', type=str, required=False)
            args = parser.parse_args()

            # Update wallet fields
            if args.get('name'):
                wallet.name = args['name']
            if args.get('description') is not None:
                wallet.description = args['description']
            if args.get('balance') is not None:
                wallet.balance = args['balance']
            if args.get('currency'):
                wallet.currency = args['currency']
            if args.get('type'):
                wallet.type = args['type']

            try:
                db.session.commit()
                return {
                    "message": "Wallet updated successfully",
                    "wallet": wallet.to_dict()
                }
            except Exception as e:
                logger.error(f"Error updating wallet: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in PUT /wallets/{wallet_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, wallet_id):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the wallet
            wallet = Wallet.query.filter_by(id=wallet_id, user_id=user_id).first()
            if not wallet:
                return {"error": "Wallet not found or access denied"}, 404

            try:
                db.session.delete(wallet)
                db.session.commit()
                return {
                    "message": "Wallet deleted successfully"
                }
            except Exception as e:
                logger.error(f"Error deleting wallet: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in DELETE /wallets/{wallet_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500
