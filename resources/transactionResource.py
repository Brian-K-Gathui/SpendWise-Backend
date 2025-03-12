from flask_restful import Resource, reqparse
from flask import g, request
from models import db, Transaction, User, Wallet, Category
from services.supabase_service import SupabaseService
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from datetime import datetime

logger = logging.getLogger(__name__)

class TransactionResource(Resource):
    def __init__(self):
        self.supabase_service = SupabaseService()

    def get(self, transaction_id=None):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # If transaction_id is provided, get that specific transaction
            if transaction_id:
                transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
                if not transaction:
                    return {"error": "Transaction not found or access denied"}, 404

                return transaction.to_dict()

            # Otherwise, return all transactions for the user with optional filtering
            query = Transaction.query.filter_by(user_id=user_id)

            # Apply filters if provided
            wallet_id = request.args.get('wallet_id')
            if wallet_id:
                query = query.filter_by(wallet_id=wallet_id)

            transaction_type = request.args.get('type')
            if transaction_type:
                query = query.filter_by(type=transaction_type)

            category_id = request.args.get('category_id')
            if category_id:
                query = query.filter_by(category_id=category_id)

            start_date = request.args.get('start_date')
            if start_date:
                query = query.filter(Transaction.date >= datetime.fromisoformat(start_date))

            end_date = request.args.get('end_date')
            if end_date:
                query = query.filter(Transaction.date <= datetime.fromisoformat(end_date))

            # Order by date descending (newest first)
            query = query.order_by(Transaction.date.desc())

            transactions = query.all()
            return [transaction.to_dict() for transaction in transactions]

        except OperationalError as e:
            logger.error(f"Database connection error in GET /transactions: {str(e)}")
            db.session.rollback()
            return {"error": "Database connection error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error in GET /transactions: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def post(self):
        try:
            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('wallet_id', type=int, required=True, help='Wallet ID is required')
            parser.add_argument('category_id', type=int, required=False)
            parser.add_argument('amount', type=float, required=True, help='Amount is required')
            parser.add_argument('type', type=str, required=True, help='Transaction type is required')
            parser.add_argument('description', type=str, required=False)
            parser.add_argument('date', type=str, required=False)
            parser.add_argument('is_recurring', type=bool, required=False, default=False)
            parser.add_argument('recurring_interval', type=str, required=False)
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

            # Check if wallet exists and belongs to user
            wallet = Wallet.query.filter_by(id=args['wallet_id'], user_id=user_id).first()
            if not wallet:
                return {"error": "Wallet not found or access denied"}, 404

            # Check if category exists if provided
            if args.get('category_id'):
                category = Category.query.get(args['category_id'])
                if not category:
                    return {"error": "Category not found"}, 404

            # Parse date if provided, otherwise use current date
            transaction_date = datetime.utcnow()

            if args.get('date'):
                try:
                    transaction_date = datetime.fromisoformat(args['date'].replace('Z', '+00:00'))
                except ValueError:
                    return {"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400

            # Create new transaction
            new_transaction = Transaction(
                user_id=user_id,
                wallet_id=args['wallet_id'],
                category_id=args.get('category_id'),
                amount=args['amount'],
                type=args['type'],
                description=args.get('description', ''),
                date=transaction_date,
                is_recurring=args.get('is_recurring', False),
                recurring_interval=args.get('recurring_interval')
            )

            # Update wallet balance
            if args['type'] == 'income':
                wallet.balance += args['amount']
            elif args['type'] == 'expense':
                wallet.balance -= args['amount']
            else:
                return {"error": "Invalid transaction type. Use 'income' or 'expense'"}, 400

            try:
                db.session.add(new_transaction)
                db.session.commit()
                return {
                    "message": "Transaction created successfully",
                    "transaction": new_transaction.to_dict(),
                    "wallet_balance": wallet.balance
                }, 201
            except Exception as e:
                logger.error(f"Error creating transaction: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in POST /transactions: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500
