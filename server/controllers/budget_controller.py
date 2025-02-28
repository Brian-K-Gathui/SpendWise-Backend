from datetime import datetime
from server.models import db, Budget

def get_all_budgets():
    budgets = [budget.serialize() for budget in Budget.query.all()]
    return budgets, 200

def get_budget_by_id(budget_id):
    budget = Budget.query.get(budget_id)
    if not budget:
        return {"error": "Budget not found"}, 404
    return budget.serialize(), 200

def create_budget(data):
    required_fields = ['user_id', 'category_id', 'wallet_id', 'amount', 'period', 'start_date']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    try:
        start_date = datetime.fromisoformat(data.get('start_date'))
    except Exception:
        return {"error": "Invalid start_date format. Please use ISO format."}, 400

    end_date = None
    if data.get('end_date'):
        try:
            end_date = datetime.fromisoformat(data.get('end_date'))
        except Exception:
            return {"error": "Invalid end_date format. Please use ISO format."}, 400

    new_budget = Budget(
        user_id=data.get('user_id'),
        category_id=data.get('category_id'),
        wallet_id=data.get('wallet_id'),
        amount=data.get('amount'),
        period=data.get('period'),
        start_date=start_date,
        end_date=end_date
    )

    db.session.add(new_budget)
    db.session.commit()
    return new_budget.serialize(), 201

def update_budget(budget_id, data):
    budget = Budget.query.get(budget_id)
    if not budget:
        return {"error": "Budget not found"}, 404

    allowed_fields = {'user_id', 'category_id', 'wallet_id', 'amount', 'period', 'start_date', 'end_date'}
    for key, value in data.items():
        if key in allowed_fields:
            if key in ['start_date', 'end_date'] and value:
                try:
                    value = datetime.fromisoformat(value)
                except Exception:
                    return {"error": f"Invalid {key} format. Please use ISO format."}, 400
            setattr(budget, key, value)
    db.session.commit()
    return budget.serialize(), 200

def delete_budget(budget_id):
    budget = Budget.query.get(budget_id)
    if not budget:
        return {"error": "Budget not found"}, 404
    db.session.delete(budget)
    db.session.commit()
    return {"message": "Budget deleted successfully"}, 200
