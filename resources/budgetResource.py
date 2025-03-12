from flask_restful import Resource, reqparse
from flask import g, request
from models import db, Budget, User, Wallet, Category
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from datetime import datetime

logger = logging.getLogger(__name__)

class BudgetResource(Resource):
    def get(self, budget_id=None):
        try:
            #  Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # If budget_id is provided, get that specific budget
            if budget_id:
                budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
                if not budget:
                    return {"error": "Budget not found or access denied"}, 404

                return budget.to_dict()

            # O return all budgets for the user with optional filtering
            query = Budget.query.filter_by(user_id=user_id)

            # Apply filters if provided
            wallet_id = request.args.get('wallet_id')
            if wallet_id:
                query = query.filter_by(wallet_id=wallet_id)

            category_id = request.args.get('category_id')
            if category_id:
                query = query.filter_by(category_id=category_id)

            period = request.args.get('period')
            if period:
                query = query.filter_by(period=period)

            # Order by start_date descending (newest first)
            query = query.order_by(Budget.start_date.desc())

            budgets = query.all()
            return [budget.to_dict() for budget in budgets]

        except OperationalError as e:
            logger.error(f"Database connection error in GET /budgets: {str(e)}")
            db.session.rollback()
            return {"error": "Database connection error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error in GET /budgets: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('wallet_id', type=int, required=True, help='Wallet ID is required')
            parser.add_argument('category_id', type=int, required=True, help='Category ID is required')
            parser.add_argument('amount', type=float, required=True, help='Amount is required')
            parser.add_argument('period', type=str, required=True, help='Period is required')
            parser.add_argument('start_date', type=str, required=True, help='Start date is required')
            parser.add_argument('end_date', type=str, required=False)
            args = parser.parse_args()

            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            # if wallet exists and belongs to user
            wallet = Wallet.query.filter_by(id=args['wallet_id'], user_id=user_id).first()
            if not wallet:
                return {"error": "Wallet not found or access denied"}, 404

            # if category exists
            category = Category.query.get(args['category_id'])
            if not category:
                return {"error": "Category not found"}, 404

            # Parse dates
            try:
                start_date = datetime.fromisoformat(args['start_date'].replace('Z', '+00:00'))
            except ValueError:
                return {"error": "Invalid start date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400

            end_date = None
            if args.get('end_date'):
                try:
                    end_date = datetime.fromisoformat(args['end_date'].replace('Z', '+00:00'))
                except ValueError:
                    return {"error": "Invalid end date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400

            # new budget
            new_budget = Budget(
                user_id=user_id,
                wallet_id=args['wallet_id'],
                category_id=args['category_id'],
                amount=args['amount'],
                period=args['period'],
                start_date=start_date,
                end_date=end_date
            )

            try:
                db.session.add(new_budget)
                db.session.commit()
                return {
                    "message": "Budget created successfully",
                    "budget": new_budget.to_dict()
                }, 201
            except Exception as e:
                logger.error(f"Error creating budget: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in POST /budgets: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, budget_id):
        try:
            # Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the budget
            budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
            if not budget:
                return {"error": "Budget not found or access denied"}, 404

            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('wallet_id', type=int, required=False)
            parser.add_argument('category_id', type=int, required=False)
            parser.add_argument('amount', type=float, required=False)
            parser.add_argument('period', type=str, required=False)
            parser.add_argument('start_date', type=str, required=False)
            parser.add_argument('end_date', type=str, required=False)
            args = parser.parse_args()

            # if wallet exists and belongs to user if wallet_id is being updated
            if args.get('wallet_id'):
                wallet = Wallet.query.filter_by(id=args['wallet_id'], user_id=user_id).first()
                if not wallet:
                    return {"error": "Wallet not found or access denied"}, 404
                budget.wallet_id = args['wallet_id']

            # Check if category exists if category_id is being updated
            if args.get('category_id'):
                category = Category.query.get(args['category_id'])
                if not category:
                    return {"error": "Category not found"}, 404
                budget.category_id = args['category_id']

            # Update other fields if provided
            if args.get('amount') is not None:
                budget.amount = args['amount']
            if args.get('period'):
                budget.period = args['period']
            if args.get('start_date'):
                try:
                    budget.start_date = datetime.fromisoformat(args['start_date'].replace('Z', '+00:00'))
                except ValueError:
                    return {"error": "Invalid start date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
            if args.get('end_date') is not None:
                if args['end_date']:
                    try:
                        budget.end_date = datetime.fromisoformat(args['end_date'].replace('Z', '+00:00'))
                    except ValueError:
                        return {"error": "Invalid end date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
                else:
                    budget.end_date = None

            try:
                db.session.commit()
                return {
                    "message": "Budget updated successfully",
                    "budget": budget.to_dict()
                }
            except Exception as e:
                logger.error(f"Error updating budget: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in PUT /budgets/{budget_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, budget_id):
        try:
            #  Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the budget
            budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
            if not budget:
                return {"error": "Budget not found or access denied"}, 404

            try:
                db.session.delete(budget)
                db.session.commit()
                return {
                    "message": "Budget deleted successfully"
                }
            except Exception as e:
                logger.error(f"Error deleting budget: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in DELETE /budgets/{budget_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500
