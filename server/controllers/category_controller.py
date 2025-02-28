from server.models import db, Category

def get_all_categories():
    categories = [category.serialize() for category in Category.query.all()]
    return categories, 200

def get_category_by_id(category_id):
    category = Category.query.get(category_id)
    if not category:
        return {"error": "Category not found"}, 404
    return category.serialize(), 200

def create_category(data):
    required_fields = ['name', 'type']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    new_category = Category(
        name=data.get('name'),
        type=data.get('type'),
        icon=data.get('icon'),
        color=data.get('color'),
        is_default=data.get('is_default', False),
        created_by=data.get('created_by')
    )

    db.session.add(new_category)
    db.session.commit()
    return new_category.serialize(), 201

def update_category(category_id, data):
    category = Category.query.get(category_id)
    if not category:
        return {"error": "Category not found"}, 404

    allowed_fields = {'name', 'type', 'icon', 'color', 'is_default'}
    for key, value in data.items():
        if key in allowed_fields:
            setattr(category, key, value)
    db.session.commit()
    return category.serialize(), 200

def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return {"error": "Category not found"}, 404
    db.session.delete(category)
    db.session.commit()
    return {"message": "Category deleted successfully"}, 200
