from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from server.config import db  # Using the initialized SQLAlchemy instance

class User(db.Model, SerializerMixin):
    """
    User Model: Represents both regular users and admins in SpendWise.

    Attributes:
    - id: Unique identifier for the user.
    - username: User's chosen username.
    - email: Unique email address for verification and notifications.
    - password_hash: Securely stored hashed password.
    - full_name: User's full name.
    - phone_number: Optional phone number for additional verification.
    - is_verified: Indicates if the user's email has been verified.
    - mfa_enabled: Tracks if multi-factor authentication is enabled.
    - role: User role; for example, 'user' or 'admin'.
    - created_at: Timestamp of account creation.
    - updated_at: Timestamp of the last update.
    """
    __tablename__ = 'users'
    serialize_rules = ('-password_hash',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    is_verified = db.Column(db.Boolean, default=False)
    mfa_enabled = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @validates('username', 'email')
    def validate_not_empty(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key.capitalize()} cannot be empty")
        if key == 'email' and '@' not in value:
            raise ValueError("Invalid email format")
        return value

    def __repr__(self):
        return f'<User {self.id}: {self.username}>'
