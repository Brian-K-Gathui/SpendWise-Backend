from flask_restful import Resource, reqparse
from flask import g, request
from models import db, Category, User
from services.supabase_service import SupabaseService
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

logger = logging.getLogger(__name__)

class CategoryResource(Resource):
    def __init__(self):
        self.supabase_service = SupabaseService()

    def get(self, category_id=None):
        try:
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            if category_id:
                category = Category.query.get(category_id)
                if not category:
                    return {"error": "Category not found"}, 404

                return category.to_dict()

            #  return all categories
            categories = Category.query.all()
            return [category.to_dict() for category in categories]

        except OperationalError as e:
            logger.error(f"Database connection error in GET /categories: {str(e)}")
            db.session.rollback()
            return {"error": "Database connection error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error in GET /categories: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=True, help='Category name is required')
            parser.add_argument('description', type=str, required=False)
            parser.add_argument('icon', type=str, required=False)
            parser.add_argument('color', type=str, required=False)
            args = parser.parse_args()

            #Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            #  if user exists in local database
            user = User.query.get(user_id)

            # If not in local database, check Supabase
            if not user:
                supabase_user = self.supabase_service.get_user_data(user_id)
                if not supabase_user:
                    # If user doesn't exist in Supabase either, create them
                    email = g.user.get('email', '')
                    self.supabase_service.create_or_update_user(user_id, email, {})

                    #  create in local database
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

            # Check if category with the same name already exists
            existing_category = Category.query.filter_by(name=args['name']).first()
            if existing_category:
                return {"error": "A category with this name already exists"}, 409

            # Create new category
            new_category = Category(
                name=args['name'],
                description=args.get('description', ''),
                icon=args.get('icon', ''),
                color=args.get('color', '#6366F1')
            )

            try:
                db.session.add(new_category)
                db.session.commit()
                return {
                    "message": "Category created successfully",
                    "category": new_category.to_dict()
                }, 201
            except Exception as e:
                logger.error(f"Error creating category: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in POST /categories: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500
