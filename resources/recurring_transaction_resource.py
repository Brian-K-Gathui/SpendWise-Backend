from flask_restful import Resource, reqparse
from flask import g, request
from models import db, RecurringTransaction, User, Wallet, Category, Transaction
from services.supabase_service import SupabaseService
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from datetime import datetime, timedelta
import dateutil.relativedelta as rd

logger = logging.getLogger(__name__)

class RecurringTransactionResource(Resource):
    def __init__(self):
        self.supabase_service = SupabaseService()

    def get(self, recurring_transaction_id=None):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # If recurring_transaction_id is provided, get that specific recurring transaction
            if recurring_transaction_id:
                recurring_transaction = RecurringTransaction.query.filter_by(id=recurring_transaction_id, user_id=user_id).first()
                if not recurring_transaction:
                    return {"error": "Recurring transaction not found or access denied"}, 404

                return recurring_transaction.to_dict()

            # Otherwise, return all recurring transactions for the user with optional filtering
            query = RecurringTransaction.query.filter_by(user_id=user_id)

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

            is_active = request.args.get('is_active')
            if is_active is not None:
                is_active_bool = is_active.lower() == 'true'
                query = query.filter_by(is_active=is_active_bool)

            # Order by next_due date
            query = query.order_by(RecurringTransaction.next_due)

            recurring_transactions = query.all()
            return [rt.to_dict() for rt in recurring_transactions]

        except OperationalError as e:
            logger.error(f"Database connection error in GET /recurring-transactions: {str(e)}")
            db.session.rollback()
            return {"error": "Database connection error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error in GET /recurring-transactions: {str(e)}")
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
            parser.add_argument('frequency', type=str, required=True, help='Frequency is required')
            parser.add_argument('start_date', type=str, required=True, help='Start date is required')
            parser.add_argument('end_date', type=str, required=False)
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

            # Check if category exists if provided
            if args.get('category_id'):
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

            # Calculate next due date based on frequency and start date
            next_due = self.calculate_next_due(start_date, args['frequency'])

            # Create new recurring transaction
            new_recurring_transaction = RecurringTransaction(
                user_id=user_id,
                wallet_id=args['wallet_id'],
                category_id=args.get('category_id'),
                amount=args['amount'],
                type=args['type'],
                description=args.get('description', ''),
                frequency=args['frequency'],
                start_date=start_date,
                end_date=end_date,
                next_due=next_due,
                is_active=True
            )

            try:
                db.session.add(new_recurring_transaction)
                db.session.commit()
                return {
                    "message": "Recurring transaction created successfully",
                    "recurring_transaction": new_recurring_transaction.to_dict()
                }, 201
            except Exception as e:
                logger.error(f"Error creating recurring transaction: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in POST /recurring-transactions: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, recurring_transaction_id):
        try:
            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('wallet_id', type=int, required=False)
            parser.add_argument('category_id', type=int, required=False)
            parser.add_argument('amount', type=float, required=False)
            parser.add_argument('type', type=str, required=False)
            parser.add_argument('description', type=str, required=False)
            parser.add_argument('frequency', type=str, required=False)
            parser.add_argument('start_date', type=str, required=False)
            parser.add_argument('end_date', type=str, required=False)
            parser.add_argument('is_active', type=bool, required=False)
            args = parser.parse_args()

            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the recurring transaction
            recurring_transaction = RecurringTransaction.query.filter_by(id=recurring_transaction_id, user_id=user_id).first()
            if not recurring_transaction:
                return {"error": "Recurring transaction not found or access denied"}, 404

            # Update fields if provided
            if args.get('wallet_id'):
                wallet = Wallet.query.filter_by(id=args['wallet_id'], user_id=user_id).first()
                if not wallet:
                    return {"error": "Wallet not found or access denied"}, 404
                recurring_transaction.wallet_id = args['wallet_id']

            if args.get('category_id') is not None:
                if args['category_id']:
                    category = Category.query.get(args['category_id'])
                    if not category:
                        return {"error": "Category not found"}, 404
                    recurring_transaction.category_id = args['category_id']
                else:
                    recurring_transaction.category_id = None

            if args.get('amount') is not None:
                recurring_transaction.amount = args['amount']

            if args.get('type'):
                recurring_transaction.type = args['type']

            if args.get('description') is not None:
                recurring_transaction.description = args['description']

            if args.get('frequency'):
                recurring_transaction.frequency = args['frequency']
                # Recalculate next_due if frequency changes
                recurring_transaction.next_due = self.calculate_next_due(
                    recurring_transaction.start_date,
                    args['frequency'],
                    recurring_transaction.last_processed
                )

            if args.get('start_date'):
                try:
                    start_date = datetime.fromisoformat(args['start_date'].replace('Z', '+00:00'))
                    recurring_transaction.start_date = start_date
                    # Recalculate next_due if start_date changes
                    recurring_transaction.next_due = self.calculate_next_due(
                        start_date,
                        recurring_transaction.frequency,
                        recurring_transaction.last_processed
                    )
                except ValueError:
                    return {"error": "Invalid start date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400

            if args.get('end_date') is not None:
                if args['end_date']:
                    try:
                        recurring_transaction.end_date = datetime.fromisoformat(args['end_date'].replace('Z', '+00:00'))
                    except ValueError:
                        return {"error": "Invalid end date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
                else:
                    recurring_transaction.end_date = None

            if args.get('is_active') is not None:
                recurring_transaction.is_active = args['is_active']

            try:
                db.session.commit()
                return {
                    "message": "Recurring transaction updated successfully",
                    "recurring_transaction": recurring_transaction.to_dict()
                }
            except Exception as e:
                logger.error(f"Error updating recurring transaction: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in PUT /recurring-transactions/{recurring_transaction_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, recurring_transaction_id):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the recurring transaction
            recurring_transaction = RecurringTransaction.query.filter_by(id=recurring_transaction_id, user_id=user_id).first()
            if not recurring_transaction:
                return {"error": "Recurring transaction not found or access denied"}, 404

            try:
                db.session.delete(recurring_transaction)
                db.session.commit()
                return {
                    "message": "Recurring transaction deleted successfully"
                }
            except Exception as e:
                logger.error(f"Error deleting recurring transaction: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in DELETE /recurring-transactions/{recurring_transaction_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def calculate_next_due(self, start_date, frequency, last_processed=None):
        """Calculate the next due date based on frequency and start date"""
        now = datetime.utcnow()

        # If there's a last processed date, calculate from that instead of start date
        base_date = last_processed if last_processed else start_date

        # If base date is in the future, return it as the next due date
        if base_date > now:
            return base_date

        # Calculate next due date based on frequency
        if frequency == 'daily':
            # Find the next day after now
            days_since = (now - base_date).days
            return base_date + timedelta(days=days_since + 1)

        elif frequency == 'weekly':
            # Find the next week after now
            weeks_since = (now - base_date).days // 7
            return base_date + timedelta(weeks=weeks_since + 1)

        elif frequency == 'monthly':
            # Find the next month after now
            months_since = (now.year - base_date.year) * 12 + now.month - base_date.month
            if now.day > base_date.day or (now.day == base_date.day and now.time() >= base_date.time()):
                months_since += 1
            return base_date + rd.relativedelta(months=months_since)

        elif frequency == 'yearly':
            # Find the next year after now
            years_since = now.year - base_date.year
            if (now.month > base_date.month or
                (now.month == base_date.month and now.day > base_date.day) or
                (now.month == base_date.month and now.day == base_date.day and now.time() >= base_date.time())):
                years_since += 1
            return base_date + rd.relativedelta(years=years_since)

        else:
            # Default to monthly if frequency is not recognized
            return base_date + rd.relativedelta(months=1)

class ProcessRecurringTransactionsResource(Resource):
    def post(self):
        try:
            # This endpoint would typically be called by a scheduled task
            # For security, we'll require an API key or admin authentication in a real app

            # Get all active recurring transactions that are due
            now = datetime.utcnow()
            due_transactions = RecurringTransaction.query.filter(
                RecurringTransaction.is_active == True,
                RecurringTransaction.next_due <= now,
                db.or_(
                    RecurringTransaction.end_date.is_(None),
                    RecurringTransaction.end_date >= now
                )
            ).all()

            processed_count = 0
            for rt in due_transactions:
                try:
                    # Create a new transaction
                    transaction = Transaction(
                        user_id=rt.user_id,
                        wallet_id=rt.wallet_id,
                        category_id=rt.category_id,
                        amount=rt.amount,
                        type=rt.type,
                        description=f"{rt.description} (Recurring)",
                        date=rt.next_due,
                        is_recurring=True,
                        recurring_interval=rt.frequency
                    )

                    # Update wallet balance
                    wallet = Wallet.query.get(rt.wallet_id)
                    if rt.type == 'income':
                        wallet.balance += rt.amount
                    elif rt.type == 'expense':
                        wallet.balance -= rt.amount

                    # Update recurring transaction
                    rt.last_processed = rt.next_due
                    rt.next_due = self.calculate_next_due(rt.start_date, rt.frequency, rt.last_processed)

                    # Check if this was the last occurrence
                    if rt.end_date and rt.next_due > rt.end_date:
                        rt.is_active = False

                    db.session.add(transaction)
                    processed_count += 1

                except Exception as e:
                    logger.error(f"Error processing recurring transaction {rt.id}: {str(e)}")
                    # Continue with other transactions
                    continue

            db.session.commit()
            return {
                "message": f"Processed {processed_count} recurring transactions",
                "processed_count": processed_count
            }

        except Exception as e:
            logger.error(f"Error in POST /recurring-transactions/process: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def calculate_next_due(self, start_date, frequency, last_processed):
        """Calculate the next due date based on frequency and last processed date"""
        if frequency == 'daily':
            return last_processed + timedelta(days=1)
        elif frequency == 'weekly':
            return last_processed + timedelta(weeks=1)
        elif frequency == 'monthly':
            return last_processed + rd.relativedelta(months=1)
        elif frequency == 'yearly':
            return last_processed + rd.relativedelta(years=1)
        else:
            # Default to monthly if frequency is not recognized
            return last_processed + rd.relativedelta(months=1)
