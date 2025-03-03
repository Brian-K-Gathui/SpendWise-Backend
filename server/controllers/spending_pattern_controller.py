from server.models import db, SpendingPattern

def get_all_spending_patterns():
    patterns = [sp.serialize() for sp in SpendingPattern.query.all()]
    return patterns, 200

def get_spending_pattern_by_id(pattern_id):
    sp = SpendingPattern.query.get(pattern_id)
    if not sp:
        return {"error": "Spending Pattern not found"}, 404
    return sp.serialize(), 200

def create_spending_pattern(data):
    required_fields = ['user_id', 'pattern_type']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_sp = SpendingPattern(
        user_id=data.get('user_id'),
        pattern_type=data.get('pattern_type'),
        pattern_data=data.get('pattern_data'),
        significance_score=data.get('significance_score'),
        recognition_params=data.get('recognition_params'),
        actions_suggested=data.get('actions_suggested')
    )
    db.session.add(new_sp)
    db.session.commit()
    return new_sp.serialize(), 201

def update_spending_pattern(pattern_id, data):
    sp = SpendingPattern.query.get(pattern_id)
    if not sp:
        return {"error": "Spending Pattern not found"}, 404
    for key, value in data.items():
        setattr(sp, key, value)
    db.session.commit()
    return sp.serialize(), 200

def delete_spending_pattern(pattern_id):
    sp = SpendingPattern.query.get(pattern_id)
    if not sp:
        return {"error": "Spending Pattern not found"}, 404
    db.session.delete(sp)
    db.session.commit()
    return {"message": "Spending Pattern deleted successfully"}, 200
