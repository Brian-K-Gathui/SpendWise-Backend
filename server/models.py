from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from server.config import db  # Using the initialized SQLAlchemy instance

# ====================================
# User Model
# ====================================
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
class User(db.Model, SerializerMixin):

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

# ====================================
# Wallet Model
# ====================================
"""
    Wallet Model: Represents a financial account or group in SpendWise.

    Attributes:
    - id: Unique identifier for the wallet.
    - name: Display name of the wallet.
    - description: Detailed description of the wallet's purpose.
    - currency: Currency used for the wallet (default: 'KES').
    - balance: Current balance of the wallet.
    - type: Indicates if the wallet is personal or shared.
    - owner_id: Reference to the user who owns the wallet.
    - created_at: Timestamp of wallet creation.
    - updated_at: Timestamp of the last wallet update.
"""
class Wallet(db.Model, SerializerMixin):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    currency = db.Column(db.String(10), default='KES')
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    type = db.Column(db.String(50))  # 'personal' or 'shared'
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    
    # Relationships
    owner = db.relationship('User', backref='wallets', lazy=True)
    transactions = db.relationship('Transaction', backref='wallet', lazy=True)
    budgets = db.relationship('Budget', backref='wallet', lazy=True)
    collaborators = db.relationship('WalletCollaborator', backref='wallet', lazy=True)

    def __repr__(self):
        return f'<Wallet {self.id}: {self.name}>'

# ====================================
# Transaction Model
# ====================================
"""
    Transaction Model: Records all financial transactions in SpendWise.

    Attributes:
    - id: Unique identifier for the transaction.
    - wallet_id: Reference to the associated wallet.
    - category_id: Reference to the transaction category.
    - amount: Transaction amount.
    - type: Transaction type, e.g. 'expense' or 'income'.
    - description: Optional details about the transaction.
    - date: When the transaction occurred.
    - is_recurring: Indicates if the transaction is recurring.
    - recurring_interval: Frequency of recurrence (daily, weekly, monthly, yearly).
    - created_by: Reference to the user who recorded the transaction.
    - created_at: Timestamp when the transaction was recorded.
    - updated_at: Timestamp of the last update.
"""
class Transaction(db.Model, SerializerMixin):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # expense or income
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_interval = db.Column(db.String(50))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

# ====================================
# Category Model
# ====================================
"""
    Category Model: Defines transaction categories in SpendWise.

    Attributes:
    - id: Unique identifier for the category.
    - name: Name of the category (e.g. "Groceries", "Salary").
    - type: Indicates if the category is for expenses or income.
    - icon: Optional icon identifier for UI.
    - color: Optional color code.
    - is_default: Indicates if this is a system default category.
    - created_by: Reference to the user who created the category (null for defaults).
    - created_at: Timestamp of category creation.
    - updated_at: Timestamp of the last category update.
"""
class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20))  # expense or income
    icon = db.Column(db.String(100))
    color = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

# ====================================
# Wallet Collaborator Model
# ====================================
"""
    Wallet Collaborator Model: Manages shared wallet access in SpendWise.

    Attributes:
    - id: Unique identifier for the collaboration.
    - wallet_id: Reference to the shared wallet.
    - user_id: Reference to the collaborating user.
    - permission_level: Access level (owner, editor, viewer).
    - created_at: Timestamp when the collaboration was established.
    - updated_at: Timestamp of the last update.
"""
class WalletCollaborator(db.Model, SerializerMixin):
    __tablename__ = 'wallet_collaborators'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_level = db.Column(db.String(20))  # owner, editor, viewer
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

# ====================================
# Budget Model
# ====================================
"""
    Budget Model: Manages spending limits and financial goals in SpendWise.

    Attributes:
    - id: Unique identifier for the budget.
    - user_id: Reference to the user who created the budget.
    - category_id: Reference to the category this budget applies to.
    - wallet_id: Reference to the wallet this budget applies to.
    - amount: Budget limit amount.
    - period: Time period for the budget (monthly, quarterly, yearly).
    - start_date: When the budget period begins.
    - end_date: When the budget period ends.
    - created_at: Timestamp when the budget was created.
    - updated_at: Timestamp of the last budget update.
"""
class Budget(db.Model, SerializerMixin):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    period = db.Column(db.String(50))  # monthly, quarterly, yearly
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())