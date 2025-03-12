from flask_restful import Resource, reqparse
from flask import g, request
from models import db, Report, User, Transaction, Budget, Category, Wallet
from services.supabase_service import SupabaseService
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

logger = logging.getLogger(__name__)

class ReportResource(Resource):
    def __init__(self):
        self.supabase_service = SupabaseService()

    def get(self, report_id=None):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # If report_id is provided, get that specific report
            if report_id:
                report = Report.query.filter_by(id=report_id, user_id=user_id).first()
                if not report:
                    return {"error": "Report not found or access denied"}, 404

                return report.to_dict()

            # Otherwise, return all reports for the user
            reports = Report.query.filter_by(user_id=user_id).order_by(Report.created_at.desc()).all()
            return [report.to_dict() for report in reports]

        except OperationalError as e:
            logger.error(f"Database connection error in GET /reports: {str(e)}")
            db.session.rollback()
            return {"error": "Database connection error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error in GET /reports: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def post(self):
        try:
            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('title', type=str, required=True, help='Title is required')
            parser.add_argument('type', type=str, required=True, help='Report type is required')
            parser.add_argument('parameters', type=dict, required=False)
            args = parser.parse_args()

            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            # Generate report data based on type and parameters
            report_data = self.generate_report_data(user_id, args['type'], args.get('parameters', {}))

            # Create new report
            new_report = Report(
                user_id=user_id,
                title=args['title'],
                type=args['type'],
                parameters=args.get('parameters', {}),
                data=report_data
            )

            try:
                db.session.add(new_report)
                db.session.commit()
                return {
                    "message": "Report generated successfully",
                    "report": new_report.to_dict()
                }, 201
            except Exception as e:
                logger.error(f"Error creating report: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in POST /reports: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, report_id):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the report
            report = Report.query.filter_by(id=report_id, user_id=user_id).first()
            if not report:
                return {"error": "Report not found or access denied"}, 404

            try:
                db.session.delete(report)
                db.session.commit()
                return {
                    "message": "Report deleted successfully"
                }
            except Exception as e:
                logger.error(f"Error deleting report: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in DELETE /reports/{report_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def generate_report_data(self, user_id, report_type, parameters):
        """Generate report data based on type and parameters"""
        try:
            # Default date range if not provided
            start_date = parameters.get('start_date')
            end_date = parameters.get('end_date')

            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                # Default to last 30 days
                start_date = datetime.utcnow() - timedelta(days=30)

            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.utcnow()

            wallet_id = parameters.get('wallet_id')
            category_id = parameters.get('category_id')

            # Base query for transactions
            query = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )

            # Apply wallet filter if provided
            if wallet_id:
                query = query.filter(Transaction.wallet_id == wallet_id)

            # Apply category filter if provided
            if category_id:
                query = query.filter(Transaction.category_id == category_id)

            if report_type == 'expense_summary':
                # Get expense transactions grouped by category
                expenses = query.filter(Transaction.type == 'expense').all()

                # Group by category
                category_totals = {}
                for expense in expenses:
                    category_name = expense.category.name if expense.category else 'Uncategorized'
                    if category_name not in category_totals:
                        category_totals[category_name] = 0
                    category_totals[category_name] += expense.amount

                # Format data for chart
                chart_data = [{'name': cat, 'value': amount} for cat, amount in category_totals.items()]

                # Calculate total expenses
                total_expenses = sum(expense.amount for expense in expenses)

                return {
                    'total_expenses': total_expenses,
                    'category_breakdown': category_totals,
                    'chart_data': chart_data,
                    'transaction_count': len(expenses),
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }

            elif report_type == 'income_summary':
                # Get income transactions grouped by category
                incomes = query.filter(Transaction.type == 'income').all()

                # Group by category
                category_totals = {}
                for income in incomes:
                    category_name = income.category.name if income.category else 'Uncategorized'
                    if category_name not in category_totals:
                        category_totals[category_name] = 0
                    category_totals[category_name] += income.amount

                # Format data for chart
                chart_data = [{'name': cat, 'value': amount} for cat, amount in category_totals.items()]

                # Calculate total income
                total_income = sum(income.amount for income in incomes)

                return {
                    'total_income': total_income,
                    'category_breakdown': category_totals,
                    'chart_data': chart_data,
                    'transaction_count': len(incomes),
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }

            elif report_type == 'budget_analysis':
                # Get budgets for the user
                budgets_query = Budget.query.filter(
                    Budget.user_id == user_id,
                    Budget.start_date <= end_date,
                    or_(Budget.end_date >= start_date, Budget.end_date.is_(None))
                )

                if wallet_id:
                    budgets_query = budgets_query.filter(Budget.wallet_id == wallet_id)

                budgets = budgets_query.all()

                budget_analysis = []
                for budget in budgets:
                    # Get expenses for this budget's category
                    expenses = Transaction.query.filter(
                        Transaction.user_id == user_id,
                        Transaction.type == 'expense',
                        Transaction.category_id == budget.category_id,
                        Transaction.date >= max(budget.start_date, start_date),
                        Transaction.date <= min(budget.end_date or end_date, end_date)
                    )

                    if wallet_id:
                        expenses = expenses.filter(Transaction.wallet_id == wallet_id)

                    total_spent = sum(expense.amount for expense in expenses.all())

                    budget_analysis.append({
                        'budget_id': budget.id,
                        'category': budget.category.name if budget.category else 'Uncategorized',
                        'budget_amount': budget.amount,
                        'spent_amount': total_spent,
                        'remaining': budget.amount - total_spent,
                        'percentage_used': (total_spent / budget.amount * 100) if budget.amount > 0 else 0,
                        'period': budget.period,
                        'start_date': budget.start_date.isoformat(),
                        'end_date': budget.end_date.isoformat() if budget.end_date else None
                    })

                return {
                    'budgets': budget_analysis,
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }

            elif report_type == 'cash_flow':
                # Get all transactions
                transactions = query.order_by(Transaction.date).all()

                # Group by date
                daily_flow = {}
                for transaction in transactions:
                    date_str = transaction.date.strftime('%Y-%m-%d')
                    if date_str not in daily_flow:
                        daily_flow[date_str] = {'income': 0, 'expense': 0, 'net': 0}

                    if transaction.type == 'income':
                        daily_flow[date_str]['income'] += transaction.amount
                    else:
                        daily_flow[date_str]['expense'] += transaction.amount

                    daily_flow[date_str]['net'] = daily_flow[date_str]['income'] - daily_flow[date_str]['expense']

                # Calculate totals
                total_income = sum(day['income'] for day in daily_flow.values())
                total_expense = sum(day['expense'] for day in daily_flow.values())
                net_flow = total_income - total_expense

                # Format for chart
                chart_data = [
                    {'date': date, 'income': data['income'], 'expense': data['expense'], 'net': data['net']}
                    for date, data in daily_flow.items()
                ]

                return {
                    'total_income': total_income,
                    'total_expense': total_expense,
                    'net_flow': net_flow,
                    'daily_flow': daily_flow,
                    'chart_data': chart_data,
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }

            else:
                return {"error": f"Unsupported report type: {report_type}"}, 400

        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            return {"error": "Failed to generate report data"}
