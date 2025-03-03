from server.models import db, SmartBudget

def get_all_smart_budgets():
    smart_budgets = [sb.serialize() for sb in SmartBudget.query.all()]
    return smart_budgets, 200

def get_smart_budget_by_id(sb_id):
    sb = SmartBudget.query.get(sb_id)
    if not sb:
        return {"error": "Smart Budget not found"}, 404
    return sb.serialize(), 200

def create_smart_budget(data):
    required_fields = ['budget_id']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_sb = SmartBudget(
        budget_id=data.get('budget_id'),
        ai_parameters=data.get('ai_parameters'),
        market_conditions=data.get('market_conditions'),
        adjustment_history=data.get('adjustment_history'),
        performance_metrics=data.get('performance_metrics'),
        suggestion_log=data.get('suggestion_log')
    )
    db.session.add(new_sb)
    db.session.commit()
    return new_sb.serialize(), 201

def update_smart_budget(sb_id, data):
    sb = SmartBudget.query.get(sb_id)
    if not sb:
        return {"error": "Smart Budget not found"}, 404
    for key, value in data.items():
        setattr(sb, key, value)
    db.session.commit()
    return sb.serialize(), 200

def delete_smart_budget(sb_id):
    sb = SmartBudget.query.get(sb_id)
    if not sb:
        return {"error": "Smart Budget not found"}, 404
    db.session.delete(sb)
    db.session.commit()
    return {"message": "Smart Budget deleted successfully"}, 200
