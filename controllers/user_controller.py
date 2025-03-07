from server.models import db, User
from flask import g
import logging

logger = logging.getLogger(__name__)

def get_all_users():
    users = [user.to_dict() for user in User.query.all()]
    return users, 200

def get_user_by_id(user_id):
    # Verify the requesting user is accessing their own data
    if g.user.get('sub') != user_id:
        return {"error": "Unauthorized access"}, 403

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404
    return user.to_dict(), 200

def create_user(data):
    # Get the Clerk user ID from the JWT token
    clerk_user_id = g.user.get('sub')
    if not clerk_user_id:
        return {"error": "User ID not found in token"}, 400

    # Check if user already exists
    existing_user = User.query.get(clerk_user_id)
    if existing_user:
        # Update existing user
        existing_user.email = data.get('email')
        if data.get('full_name'):
            existing_user.full_name = data.get('full_name')

        db.session.commit()
        return existing_user.to_dict(), 200

    # Create new user
    if not data.get('email'):
        return {"error": "Email is required"}, 400

    new_user = User(
        id=clerk_user_id,
        email=data.get('email'),
        full_name=data.get('full_name')
    )

    db.session.add(new_user)
    db.session.commit()
    return new_user.to_dict(), 201

def update_user(user_id, data):
    # Verify the requesting user is updating their own data
    if g.user.get('sub') != user_id:
        return {"error": "Unauthorized access"}, 403

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    allowed_fields = {'email', 'full_name', 'is_active'}
    for key, value in data.items():
        if key not in allowed_fields:
            continue
        setattr(user, key, value)

    db.session.commit()
    return user.to_dict(), 200

def delete_user(user_id):
    # Verify the requesting user is deleting their own data
    if g.user.get('sub') != user_id:
        return {"error": "Unauthorized access"}, 403

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted successfully"}, 200
