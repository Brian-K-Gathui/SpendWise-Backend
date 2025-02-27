# server/controllers/user_controller.py
from server.models import db, User

def get_all_users():
    users = [user.serialize() for user in User.query.all()]
    return users, 200

def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404
    return user.serialize(), 200

def create_user(data):
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field.capitalize()} is required"}, 400

    if User.query.filter_by(username=data.get('username')).first():
        return {"error": "Username already exists"}, 400
    if User.query.filter_by(email=data.get('email')).first():
        return {"error": "Email already registered"}, 400

    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        full_name=data.get('full_name'),
        phone_number=data.get('phone_number'),
        role=data.get('role', 'user')  # Default to 'user' if not provided
    )
    new_user.set_password(data.get('password'))
    db.session.add(new_user)
    db.session.commit()
    return new_user.serialize(), 201

def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    # Whitelist allowed fields for update
    allowed_fields = {'username', 'email', 'full_name', 'phone_number', 'password'}
    for key, value in data.items():
        if key not in allowed_fields:
            continue  # Skip any fields not permitted for update
        if key == 'password':
            user.set_password(value)
        else:
            setattr(user, key, value)
    db.session.commit()
    return user.serialize(), 200

def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted successfully"}, 200
