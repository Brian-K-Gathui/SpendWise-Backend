from flask_restful import Resource
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timezone
from models import db, User, TokenBlocklist
import logging

# Configure logger
logger = logging.getLogger(__name__)

class UserRegistrationResource(Resource):
    """Resource for handling user registration."""

    def post(self):
        """Register a new user."""
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['username', 'email', 'password', 'full_name']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {"message": f"Missing required fields: {', '.join(missing_fields)}"}, 400

            # Check if user already exists
            if User.query.filter_by(email=data['email']).first():
                return {"message": "User with this email already exists"}, 409

            if User.query.filter_by(username=data['username']).first():
                return {"message": "Username already taken"}, 409

            # Create new user
            new_user = User(
                username=data['username'],
                email=data['email'],
                full_name=data['full_name'],
                phone_number=data.get('phone_number'),
                is_verified=False,
                mfa_enabled=False,
                role='user'
            )
            new_user.set_password(data['password'])

            db.session.add(new_user)
            db.session.commit()

            # Generate access token
            access_token = create_access_token(identity=new_user.id)

            return {
                "message": "User registered successfully",
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "role": new_user.role
                },
                "access_token": access_token
            }, 201

        except Exception as e:
            logger.error(f"Error in user registration: {str(e)}")
            db.session.rollback()
            return {"message": f"Registration failed: {str(e)}"}, 500


class LoginResource(Resource):
    """Resource for handling user login."""

    def post(self):
        """Authenticate a user and return an access token."""
        try:
            data = request.get_json()

            # Validate required fields
            if 'email' not in data or 'password' not in data:
                return {"message": "Email and password are required"}, 400

            # Find user by email
            user = User.query.filter_by(email=data['email']).first()

            # Check if user exists and password is correct
            if not user or not user.check_password(data['password']):
                return {"message": "Invalid email or password"}, 401

            # Generate access token
            access_token = create_access_token(identity=user.id)

            # Update last login time
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            return {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role
                },
                "access_token": access_token
            }, 200

        except Exception as e:
            logger.error(f"Error in login: {str(e)}")
            return {"message": f"Login failed: {str(e)}"}, 500


class LogoutResource(Resource):
    """Resource for handling user logout."""

    @jwt_required()
    def post(self):
        """Invalidate the user's JWT token."""
        try:
            jti = get_jwt()["jti"]
            now = datetime.now(timezone.utc)

            # Add token to blocklist
            db.session.add(TokenBlocklist(jti=jti, created_at=now))
            db.session.commit()

            return {"message": "Successfully logged out"}, 200

        except Exception as e:
            logger.error(f"Error in logout: {str(e)}")
            db.session.rollback()
            return {"message": f"Logout failed: {str(e)}"}, 500


class RefreshTokenResource(Resource):
    """Resource for refreshing JWT tokens."""

    @jwt_required(refresh=True)
    def post(self):
        """Issue a new access token using a valid refresh token."""
        try:
            identity = get_jwt_identity()
            access_token = create_access_token(identity=identity)

            return {"access_token": access_token}, 200

        except Exception as e:
            logger.error(f"Error in token refresh: {str(e)}")
            return {"message": f"Token refresh failed: {str(e)}"}, 500


class UserResource(Resource):
    """Resource for user CRUD operations."""

    def get(self, user_id=None):
        """
        Get user information.

        Args:
            user_id: If provided, returns specific user, otherwise returns all users
        """
        try:
            # If user_id is provided, get that specific user
            if user_id:
                user = User.query.get(user_id)
                if not user:
                    return {"message": "User not found"}, 404

                return {"user": user.to_dict()}, 200

            # If no user_id, return all users
            users = User.query.all()
            return {"users": [user.to_dict() for user in users]}, 200

        except Exception as e:
            logger.error(f"Error retrieving user(s): {str(e)}")
            return {"message": f"Failed to retrieve user(s): {str(e)}"}, 500

    def put(self, user_id):
        """
        Update user information.

        Args:
            user_id: ID of the user to update
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404

            data = request.get_json()
            if not data:
                return {"message": "No update data provided"}, 400

            # Update user fields
            if 'username' in data:
                # Check if username is already taken by another user
                existing_user = User.query.filter_by(username=data['username']).first()
                if existing_user and existing_user.id != user_id:
                    return {"message": "Username already taken"}, 409
                user.username = data['username']

            if 'email' in data:
                # Check if email is already taken by another user
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != user_id:
                    return {"message": "Email already in use"}, 409
                user.email = data['email']

            if 'full_name' in data:
                user.full_name = data['full_name']

            if 'phone_number' in data:
                user.phone_number = data['phone_number']

            if 'password' in data and data['password']:
                user.set_password(data['password'])

            if 'role' in data:
                user.role = data['role']

            db.session.commit()

            return {
                "message": "User updated successfully",
                "user": user.to_dict()
            }, 200

        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            db.session.rollback()
            return {"message": f"Failed to update user: {str(e)}"}, 500

    def delete(self, user_id):
        """
        Delete a user.

        Args:
            user_id: ID of the user to delete
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404

            db.session.delete(user)
            db.session.commit()

            return {"message": "User deleted successfully"}, 200

        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            db.session.rollback()
            return {"message": f"Failed to delete user: {str(e)}"}, 500
