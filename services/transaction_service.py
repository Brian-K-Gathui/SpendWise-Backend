import logging
from models import db, Transaction, Wallet, Budget, Notification
from datetime import datetime
from services.budget_service import BudgetService

logger = logging.getLogger(__name__)

class TransactionService:
    @staticmethod
    def create_transaction(user_id, wallet_id, category_id, amount, transaction_type, description=None, date=None):
        """
        Create a new transaction and update wallet balance
        Returns the created transaction or None if an error occurs
        """
        try:
            # Check if wallet exists and belongs to user
            wallet = Wallet.query.filter_by(id=wallet_id, user_id=user_id).first()
            if not wallet:
                logger.error(f"Wallet {wallet_id} not found or doesn't belong to user {user_id}")
                return None

            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                wallet_id=wallet_id,
                category_id=category_id,
                amount=amount,
                type=transaction_type,
                description=description,
                date=date or datetime.utcnow()
            )

            # Update wallet balance
            if transaction_type == 'income':
                wallet.balance += amount
            elif transaction_type == 'expense':
                wallet.balance -= amount
            else:
                logger.error(f"Invalid transaction type: {transaction_type}")
                return None

            # Save transaction and updated wallet
            db.session.add(transaction)
            db.session.commit()

            # Check budget limits after adding a transaction
            if transaction_type == 'expense' and category_id:
                BudgetService.check_budget_limits(user_id)

            return transaction

        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def delete_transaction(transaction_id, user_id):
        """
        Delete a transaction and update wallet balance
        Returns True if successful, False otherwise
        """
        try:
            # Find transaction and verify ownership
            transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
            if not transaction:
                logger.error(f"Transaction {transaction_id} not found or doesn't belong to user {user_id}")
                return False

            # Get wallet
            wallet = Wallet.query.get(transaction.wallet_id)
            if not wallet:
                logger.error(f"Wallet {transaction.wallet_id} not found")
                return False

            # Update wallet balance (reverse the original transaction)
            if transaction.type == 'income':
                wallet.balance -= transaction.amount
            elif transaction.type == 'expense':
                wallet.balance += transaction.amount

            # Delete transaction
            db.session.delete(transaction)
            db.session.commit()

            return True

        except Exception as e:
            logger.error(f"Error deleting transaction: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def get_transactions_by_period(user_id, period, wallet_id=None, category_id=None):
        """
        Get transactions for a specific period (daily, weekly, monthly, yearly)
        Returns a list of transactions
        """
        try:
            # Determine date range based on period
            now = datetime.utcnow()

            if period == 'daily':
                start_date = datetime(now.year, now.month, now.day, 0, 0, 0)
            elif period == 'weekly':
                # Start from the beginning of the week (Monday)
                days_since_monday = now.weekday()
                start_date = datetime(now.year, now.month, now.day, 0, 0, 0) - timedelta(days=days_since_monday)
            elif period == 'monthly':
                start_date = datetime(now.year, now.month, 1, 0, 0, 0)
            elif period == 'yearly':
                start_date = datetime(now.year, 1, 1, 0, 0, 0)
            else:
                logger.error(f"Invalid period: {period}")
                return []

            # Build query
            query = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= now
            )

            # Apply additional filters if provided
            if wallet_id:
                query = query.filter(Transaction.wallet_id == wallet_id)

            if category_id:
                query = query.filter(Transaction.category_id == category_id)

            # Order by date descending
            query = query.order_by(Transaction.date.desc())

            return query.all()

        except Exception as e:
            logger.error(f"Error getting transactions by period: {str(e)}")
            return []
