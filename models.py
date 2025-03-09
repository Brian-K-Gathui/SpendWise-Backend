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

    id = Column(String(255), primary_key=True)  # This will store the Clerk user ID
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

    # Serialization configuration
    serialize_rules = ('-wallets.user', '-transactions.user', '-budgets.user', '-notifications.user')

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

    # Serialization configuration
    serialize_rules = ('-user.wallets', '-transactions.wallet', '-budgets.wallet')

    def to_dict(self):
        """Custom to_dict method to avoid recursion issues"""
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

    # Serialization configuration
    serialize_rules = ('-transactions.category', '-budgets.category')

    def to_dict(self):
        """Custom to_dict method to avoid recursion issues"""
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
        """Custom to_dict method to avoid recursion issues"""
        category_data = None
        if self.category:
            category_data = {
                'id': self.category.id,
                'name': self.category.name,
                'type': self.category.type,
                'icon': self.category.icon,
                'color': self.category.color
            }

        wallet_data = None
        if self.wallet:
            wallet_data = {
                'id': self.wallet.id,
                'name': self.wallet.name,
                'currency': self.wallet.currency
            }

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
        """Custom to_dict method to avoid recursion issues"""
        category_data = None
        if self.category:
            category_data = {
                'id': self.category.id,
                'name': self.category.name,
                'type': self.category.type,
                'icon': self.category.icon,
                'color': self.category.color
            }

        wallet_data = None
        if self.wallet:
            wallet_data = {
                'id': self.wallet.id,
                'name': self.wallet.name,
                'currency': self.wallet.currency
            }

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
        """Custom to_dict method to avoid recursion issues"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
