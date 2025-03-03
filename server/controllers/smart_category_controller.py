from server.models import db, SmartCategory

def get_all_smart_categories():
    smart_categories = [sc.serialize() for sc in SmartCategory.query.all()]
    return smart_categories, 200

def get_smart_category_by_id(sc_id):
    sc = SmartCategory.query.get(sc_id)
    if not sc:
        return {"error": "Smart Category not found"}, 404
    return sc.serialize(), 200

def create_smart_category(data):
    required_fields = ['name']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_sc = SmartCategory(
        name=data.get('name'),
        parent_category_id=data.get('parent_category_id'),
        rules_set=data.get('rules_set'),
        learning_threshold=data.get('learning_threshold'),
        confidence_minimum=data.get('confidence_minimum')
    )
    db.session.add(new_sc)
    db.session.commit()
    return new_sc.serialize(), 201

def update_smart_category(sc_id, data):
    sc = SmartCategory.query.get(sc_id)
    if not sc:
        return {"error": "Smart Category not found"}, 404
    for key, value in data.items():
        setattr(sc, key, value)
    db.session.commit()
    return sc.serialize(), 200

def delete_smart_category(sc_id):
    sc = SmartCategory.query.get(sc_id)
    if not sc:
        return {"error": "Smart Category not found"}, 404
    db.session.delete(sc)
    db.session.commit()
    return {"message": "Smart Category deleted successfully"}, 200
