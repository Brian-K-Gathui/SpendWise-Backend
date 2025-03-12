from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import MetaData, Column, String, DateTime, Boolean, Float, Integer, ForeignKey, Text, JSON, BigInteger, func, text
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class UserData(db.Model):
    __tablename__ = 'user_data'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Text, unique=True, nullable=False, server_default=text("requesting_user_id()"))
    email = Column(Text, nullable=True)
    data = Column(JSON, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'data': self.data,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = Column(String(255), primary_key=True)  #  store the Clerk user ID
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    recurring_transactions = relationship("RecurringTransaction", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    shared_wallets_owned = relationship("SharedWallet", foreign_keys="SharedWallet.owner_id", back_populates="owner", cascade="all, delete-orphan")
    shared_wallets_access = relationship("SharedWallet", foreign_keys="SharedWallet.member_id", back_populates="member", cascade="all, delete-orphan")

    # Serialization configuration
    serialize_rules = ('-wallets.user', '-transactions.user', '-budgets.user', '-notifications.user',
                       '-recurring_transactions.user', '-reports.user', '-shared_wallets_owned.owner', '-shared_wallets_access.member')

    def __init__(self, id, email, full_name=None):
        self.id = id
        self.email = email
        self.full_name = full_name

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class Wallet(db.Model, SerializerMixin):
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    balance = Column(Float, default=0.0)
    currency = Column(String(3), default="KES")
    type = Column(String(50), default="personal")  # personal, shared, savings, investment
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="wallet", cascade="all, delete-orphan")
    recurring_transactions = relationship("RecurringTransaction", back_populates="wallet", cascade="all, delete-orphan")
    shared_with = relationship("SharedWallet", back_populates="wallet", cascade="all, delete-orphan")

    # Serialization configuration
    serialize_rules = ('-user.wallets', '-transactions.wallet', '-budgets.wallet',
                       '-recurring_transactions.wallet', '-shared_with.wallet')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'balance': self.balance,
            'currency': self.currency,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # income, expense
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    recurring_transactions = relationship("RecurringTransaction", back_populates="category")

    # Serialization configuration
    serialize_rules = ('-transactions.category', '-budgets.category', '-recurring_transactions.category')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Transaction(db.Model, SerializerMixin):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    amount = Column(Float, nullable=False)
    type = Column(String(50), nullable=False)  # income, expense
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_recurring = Column(Boolean, default=False)
    recurring_interval = Column(String(50), nullable=True)  # daily, weekly, monthly, yearly
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    # Serialization configuration
    serialize_rules = ('-user.transactions', '-wallet.transactions', '-category.transactions')

    def to_dict(self):
        category_data = self.category.to_dict() if self.category else None
        wallet_data = self.wallet.to_dict() if self.wallet else None

        return {
            'id': self.id,
            'user_id': self.user_id,
            'wallet_id': self.wallet_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'type': self.type,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'is_recurring': self.is_recurring,
            'recurring_interval': self.recurring_interval,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category': category_data,
            'wallet': wallet_data
        }

class Budget(db.Model, SerializerMixin):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    amount = Column(Float, nullable=False)
    period = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="budgets")
    wallet = relationship("Wallet", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    # Serialization configuration
    serialize_rules = ('-user.budgets', '-wallet.budgets', '-category.budgets')

    def to_dict(self):
        category_data = self.category.to_dict() if self.category else None
        wallet_data = self.wallet.to_dict() if self.wallet else None

        return {
            'id': self.id,
            'user_id': self.user_id,
            'wallet_id': self.wallet_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'period': self.period,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category': category_data,
            'wallet': wallet_data
        }

class Notification(db.Model, SerializerMixin):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # budget_alert, shared_wallet_invite, security_alert
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")

    # Serialization configuration
    serialize_rules = ('-user.notifications',)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RecurringTransaction(db.Model, SerializerMixin):
    __tablename__ = 'recurring_transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    amount = Column(Float, nullable=False)
    type = Column(String(50), nullable=False)  # income, expense
    description = Column(Text, nullable=True)
    frequency = Column(String(50), nullable=False)  # daily, weekly, monthly, yearly
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    last_processed = Column(DateTime, nullable=True)
    next_due = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="recurring_transactions")
    wallet = relationship("Wallet", back_populates="recurring_transactions")
    category = relationship("Category", back_populates="recurring_transactions")

    # Serialization configuration
    serialize_rules = ('-user.recurring_transactions', '-wallet.recurring_transactions', '-category.recurring_transactions')

    def to_dict(self):
        category_data = self.category.to_dict() if self.category else None
        wallet_data = self.wallet.to_dict() if self.wallet else None

        return {
            'id': self.id,
            'user_id': self.user_id,
            'wallet_id': self.wallet_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'type': self.type,
            'description': self.description,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'last_processed': self.last_processed.isoformat() if self.last_processed else None,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category': category_data,
            'wallet': wallet_data
        }

class Report(db.Model, SerializerMixin):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # expense_summary, income_summary, budget_analysis, etc.
    parameters = Column(JSON, nullable=True)  # Store report parameters like date range, categories, etc.
    data = Column(JSON, nullable=True)  # Store the generated report data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reports")

    # Serialization configuration
    serialize_rules = ('-user.reports',)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'type': self.type,
            'parameters': self.parameters,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SharedWallet(db.Model, SerializerMixin):
    __tablename__ = 'shared_wallets'

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)
    owner_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    member_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    permission = Column(String(50), default="viewer")  # owner, editor, viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wallet = relationship("Wallet", back_populates="shared_with")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="shared_wallets_owned")
    member = relationship("User", foreign_keys=[member_id], back_populates="shared_wallets_access")

    # Serialization configuration
    serialize_rules = ('-wallet.shared_with', '-owner.shared_wallets_owned', '-member.shared_wallets_access')

    def to_dict(self):
        wallet_data = self.wallet.to_dict() if self.wallet else None
        member_data = self.member.to_dict() if self.member else None

        return {
            'id': self.id,
            'wallet_id': self.wallet_id,
            'owner_id': self.owner_id,
            'member_id': self.member_id,
            'permission': self.permission,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'wallet': wallet_data,
            'member': member_data
        }
