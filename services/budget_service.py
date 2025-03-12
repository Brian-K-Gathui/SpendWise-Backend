import logging
from models import db, Budget, Transaction, Notification
from datetime import datetime
from sqlalchemy import func

logger = logging.getLogger(__name__)

class BudgetService:
    @staticmethod
    def check_budget_limits(user_id):
        """
        Check if any budgets are approaching or exceeding their limits
        and create notifications if needed
        """
        try:
            # Get all active budgets for the user
            current_date = datetime.utcnow()
            budgets = Budget.query.filter(
                Budget.user_id == user_id,
                Budget.start_date <= current_date,
                (Budget.end_date >= current_date) | (Budget.end_date.is_(None))
            ).all()

            notifications_created = 0

            for budget in budgets:
                # Calculate total spent for this budget's category
                total_spent = db.session.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id == user_id,
                    Transaction.wallet_id == budget.wallet_id,
                    Transaction.category_id == budget.category_id,
                    Transaction.type == 'expense',
                    Transaction.date >= budget.start_date,
                    Transaction.date <= current_date
                ).scalar() or 0

                # Calculate percentage of budget used
                percentage_used = (total_spent / budget.amount) * 100 if budget.amount > 0 else 0

                # Check if budget is approaching or exceeding limit
                if percentage_used >= 90 and percentage_used < 100:
                    # Check if a notification already exists for this budget approaching limit
                    existing_notification = Notification.query.filter(
                        Notification.user_id == user_id,
                        Notification.type == 'budget_alert',
                        Notification.title.like(f"Budget Alert: {budget.category.name} - Approaching Limit%")
                    ).first()

                    if not existing_notification:
                        # Create approaching limit notification
                        notification = Notification(
                            user_id=user_id,
                            title=f"Budget Alert: {budget.category.name} - Approaching Limit",
                            message=f"You've used {percentage_used:.1f}% of your {budget.period} budget for {budget.category.name}.",
                            type='budget_alert'
                        )
                        db.session.add(notification)
                        notifications_created += 1

                elif percentage_used >= 100:
                    # Check if a notification already exists for this budget exceeding limit
                    existing_notification = Notification.query.filter(
                        Notification.user_id == user_id,
                        Notification.type == 'budget_alert',
                        Notification.title.like(f"Budget Alert: {budget.category.name} - Limit Exceeded%")
                    ).first()

                    if not existing_notification:
                        # Create exceeding limit notification
                        notification = Notification(
                            user_id=user_id,
                            title=f"Budget Alert: {budget.category.name} - Limit Exceeded",
                            message=f"You've exceeded your {budget.period} budget for {budget.category.name} by {percentage_used - 100:.1f}%.",
                            type='budget_alert'
                        )
                        db.session.add(notification)
                        notifications_created += 1

            if notifications_created > 0:
                db.session.commit()

            return notifications_created

        except Exception as e:
            logger.error(f"Error checking budget limits: {str(e)}")
            db.session.rollback()
            return 0

    @staticmethod
    def calculate_budget_progress(budget_id):
        """
        Calculate the current progress of a budget
        Returns a dictionary with amount, spent, remaining, and percentage
        """
        try:
            budget = Budget.query.get(budget_id)
            if not budget:
                return None

            # Calculate total spent for this budget's category
            current_date = datetime.utcnow()
            start_date = budget.start_date
            end_date = budget.end_date or current_date

            if current_date < start_date:
                # Budget period hasn't started yet
                return {
                    'budget_id': budget.id,
                    'amount': budget.amount,
                    'spent': 0,
                    'remaining': budget.amount,
                    'percentage': 0,
                    'status': 'not_started'
                }

            # Adjust end_date if it's in the future
            if end_date > current_date:
                end_date = current_date

            total_spent = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == budget.user_id,
                Transaction.wallet_id == budget.wallet_id,
                Transaction.category_id == budget.category_id,
                Transaction.type == 'expense',
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).scalar() or 0

            remaining = budget.amount - total_spent
            percentage = (total_spent / budget.amount) * 100 if budget.amount > 0 else 0

            # Determine status
            status = 'on_track'
            if percentage >= 100:
                status = 'exceeded'
            elif percentage >= 90:
                status = 'warning'

            return {
                'budget_id': budget.id,
                'amount': budget.amount,
                'spent': total_spent,
                'remaining': remaining,
                'percentage': percentage,
                'status': status
            }

        except Exception as e:
            logger.error(f"Error calculating budget progress: {str(e)}")
            return None
