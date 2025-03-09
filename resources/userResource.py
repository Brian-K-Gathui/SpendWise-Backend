from flask_restful import Resource, reqparse
from flask import g, request
from models import db, User, UserData
from services.supabase_service import SupabaseService
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

logger = logging.getLogger(__name__)

class UserResource(Resource):
    def __init__(self):
        self.supabase_service = SupabaseService()

    def get(self, user_id=None):
        try:
            # If user_id is provided, get that specific user
            if user_id:
                # Verify the requesting user is accessing their own data
                if g.user.get('sub') != user_id:
                    return {"error": "Unauthorized access"}, 403

                # First check local database
                user = User.query.get(user_id)

                # If not found in local database, check Supabase
                if not user:
                    supabase_user = self.supabase_service.get_user_data(user_id)
                    if supabase_user:
                        return {
                            'id': supabase_user['user_id'],
                            'email': supabase_user['email'],
                            'data': supabase_user['data'],
                            'created_at': supabase_user['created_at']
                        }
                    return {"error": "User not found"}, 404

                # Convert to dict
                return user.to_dict()

            # Otherwise, return all users (admin only in a real app)
            users = User.query.all()
            return [user.to_dict() for user in users]

        except OperationalError as e:
            logger.error(f"Database connection error in GET /users: {str(e)}")
            db.session.rollback()
            return {"error": "Database connection error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error in GET /users: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def post(self):
        try:
            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, required=True, help='Email is required')
            parser.add_argument('full_name', type=str, required=False)
            parser.add_argument('data', type=dict, required=False)
            args = parser.parse_args()

            # Get the Clerk user ID from the JWT token
            clerk_user_id = g.user.get('sub')
            if not clerk_user_id:
                return {"error": "User ID not found in token"}, 400

            # Create or update user in Supabase
            data = args.get('data', {})
            if args.get('full_name'):
                data['full_name'] = args['full_name']

            supabase_result = self.supabase_service.create_or_update_user(
                clerk_user_id,
                args['email'],
                data
            )

            if not supabase_result:
                return {"error": "Failed to create or update user in Supabase"}, 500

            # Check if user exists in local database
            try:
                existing_user = User.query.get(clerk_user_id)
            except OperationalError as e:
                logger.error(f"Database connection error when checking existing user: {str(e)}")
                db.session.rollback()
                return {"error": "Database connection error. Please try again later."}, 503

            if existing_user:
                # Update existing user
                existing_user.email = args['email']
                if args.get('full_name'):
                    existing_user.full_name = args['full_name']

                try:
                    db.session.commit()
                    return {
                        "message": "User updated successfully",
                        "user": existing_user.to_dict()
                    }
                except OperationalError as e:
                    logger.error(f"Database connection error when updating user: {str(e)}")
                    db.session.rollback()
                    return {"error": "Database connection error. Please try again later."}, 503
                except Exception as e:
                    logger.error(f"Error updating user: {str(e)}")
                    db.session.rollback()
                    return {"error": str(e)}, 500

            # Create new user in local database
            new_user = User(
                id=clerk_user_id,
                email=args['email'],
                full_name=args.get('full_name')
            )

            try:
                db.session.add(new_user)
                db.session.commit()
                return {
                    "message": "User created successfully",
                    "user": new_user.to_dict()
                }, 201
            except IntegrityError as e:
                logger.error(f"Integrity error when creating user: {str(e)}")
                db.session.rollback()
                return {"error": "A user with this email already exists."}, 409
            except OperationalError as e:
                logger.error(f"Database connection error when creating user: {str(e)}")
                db.session.rollback()
                return {"error": "Database connection error. Please try again later."}, 503
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in POST /users: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500
