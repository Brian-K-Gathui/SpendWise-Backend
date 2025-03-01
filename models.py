from datetime import datetime
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, JSON, Enum, Text, types, func, Column, Float, ForeignKey, Integer, String, DateTime, Boolean, Numeric
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship, validates
from werkzeug.security import generate_password_hash, check_password_hash

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    is_verified = db.Column(db.Boolean, default=False)
    mfa_enabled = db.Column(db.Boolean, default=False)
    role = db.Column(Enum('admin', 'user', name='user_roles'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    wallets = relationship('Wallet', back_populates='owner', cascade='all, delete-orphan')
    transactions = relationship('Transaction', foreign_keys='Transaction.created_by', back_populates='creator')
    budgets = relationship('Budget', back_populates='user')
    collaborations = relationship('WalletCollaborator', back_populates='user')
    categories = relationship('Category', back_populates='creator')
    notifications = relationship('Notification', back_populates='user')
    wallet_invitations = relationship('WalletInvitation', foreign_keys='WalletInvitation.invited_by', back_populates='inviter')
    ai_profile = relationship('AIAdvisorProfile', uselist=False, back_populates='user')
    receipt_scans = relationship('ReceiptScan', back_populates='user')
    financial_forecasts = relationship('FinancialForecast', back_populates='user')
    voice_transactions = relationship('VoiceTransaction', back_populates='user')
    spending_patterns = relationship('SpendingPattern', back_populates='user')
    crypto_wallets = relationship('CryptoWallet', back_populates='user')
    financial_benchmarks = relationship('FinancialBenchmark', back_populates='user')
    xr_visualizations = relationship('XRVisualization', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @validates('username', 'email')
    def validate_fields(self, key, value):
        if not value:
            raise ValueError(f"{key} cannot be empty")
        if key == 'email' and '@' not in value:
            raise ValueError("Invalid email format")
        return value

class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(Text)
    currency = db.Column(db.String(3), default='KES')
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    type = db.Column(Enum('personal', 'shared', name='wallet_type'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    owner = relationship('User', back_populates='wallets')
    transactions = relationship('Transaction', back_populates='wallet', cascade='all, delete-orphan')
    budgets = relationship('Budget', back_populates='wallet', cascade='all, delete-orphan')
    collaborators = relationship('WalletCollaborator', back_populates='wallet', cascade='all, delete-orphan')
    invitations = relationship('WalletInvitation', back_populates='wallet')
    financial_forecasts = relationship('FinancialForecast', back_populates='wallet')

class WalletCollaborator(db.Model):
    __tablename__ = 'wallet_collaborators'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_level = db.Column(Enum('owner', 'editor', 'viewer', name='permission_level'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    wallet = relationship('Wallet', back_populates='collaborators')
    user = relationship('User', back_populates='collaborations')

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(Enum('expense', 'income', name='category_type'), nullable=False)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7))  # Hex color code
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    creator = relationship('User', back_populates='categories')
    transactions = relationship('Transaction', back_populates='category')
    budgets = relationship('Budget', back_populates='category')
    smart_categories = relationship('SmartCategory', back_populates='parent_category')

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(Enum('expense', 'income', name='transaction_type'), nullable=False)
    description = db.Column(Text)
    date = db.Column(db.DateTime, nullable=False)
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_interval = db.Column(Enum('daily', 'weekly', 'monthly', 'yearly', name='recurring_interval'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    wallet = relationship('Wallet', back_populates='transactions')
    category = relationship('Category', back_populates='transactions')
    creator = relationship('User', foreign_keys=[created_by], back_populates='transactions')

class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    period = db.Column(Enum('monthly', 'quarterly', 'yearly', name='budget_period'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    user = relationship('User', back_populates='budgets')
    category = relationship('Category', back_populates='budgets')
    wallet = relationship('Wallet', back_populates='budgets')
    smart_budget = relationship('SmartBudget', uselist=False, back_populates='budget')

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(Enum('budget_alert', 'shared_wallet_invite', 'security_alert', name='notification_type'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=func.now())

    # Relationships
    user = relationship('User', back_populates='notifications')

class WalletInvitation(db.Model):
    __tablename__ = 'wallet_invitations'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invited_email = db.Column(db.String(120), nullable=False)
    permission_level = db.Column(Enum('owner', 'editor', 'viewer', name='invitation_permission_level'), nullable=False)
    status = db.Column(Enum('pending', 'accepted', 'rejected', name='invitation_status'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    expires_at = db.Column(db.DateTime, nullable=False)

    # Relationships
    wallet = relationship('Wallet', back_populates='invitations')
    inviter = relationship('User', foreign_keys=[invited_by], back_populates='wallet_invitations')

# AI-related models
class AIAdvisorProfile(db.Model):
    __tablename__ = 'ai_advisor_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    risk_tolerance = db.Column(db.Float)
    financial_goals = db.Column(JSON)
    investment_preferences = db.Column(JSON)
    learning_parameters = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    user = relationship('User', back_populates='ai_profile')

class ReceiptScan(db.Model):
    __tablename__ = 'receipt_scans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255))
    ocr_text = db.Column(Text)
    confidence_score = db.Column(db.Float)
    merchant_name = db.Column(db.String(100))
    purchase_date = db.Column(db.DateTime)
    items_detected = db.Column(JSON)
    total_amount = db.Column(db.Numeric(10, 2))
    status = db.Column(Enum('processing', 'completed', 'failed', name='receipt_scan_status'))
    created_at = db.Column(db.DateTime, default=func.now())
    processed_at = db.Column(db.DateTime)

    # Relationships
    user = relationship('User', back_populates='receipt_scans')

class FinancialForecast(db.Model):
    __tablename__ = 'financial_forecasts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    forecast_type = db.Column(Enum('spending', 'income', 'savings', 'investment', name='forecast_type'))
    time_range = db.Column(Enum('weekly', 'monthly', 'quarterly', 'yearly', name='forecast_time_range'))
    prediction_data = db.Column(JSON)
    confidence_interval = db.Column(JSON)
    model_version = db.Column(db.String(50))
    accuracy_metrics = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=func.now())
    valid_until = db.Column(db.DateTime)

    # Relationships
    user = relationship('User', back_populates='financial_forecasts')
    wallet = relationship('Wallet', back_populates='financial_forecasts')

class SmartCategory(db.Model):
    __tablename__ = 'smart_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    rules_set = db.Column(JSON)
    learning_threshold = db.Column(db.Float)
    confidence_minimum = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    parent_category = relationship('Category', back_populates='smart_categories')

class VoiceTransaction(db.Model):
    __tablename__ = 'voice_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    audio_url = db.Column(db.String(255))
    transcription = db.Column(Text)
    intent_analysis = db.Column(JSON)
    extracted_data = db.Column(JSON)
    confidence_score = db.Column(db.Float)
    status = db.Column(Enum('processing', 'completed', 'failed', name='voice_transaction_status'))
    created_at = db.Column(db.DateTime, default=func.now())
    processed_at = db.Column(db.DateTime)

    # Relationships
    user = relationship('User', back_populates='voice_transactions')

class SpendingPattern(db.Model):
    __tablename__ = 'spending_patterns'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pattern_type = db.Column(Enum('habit', 'anomaly', 'opportunity', name='pattern_type'))
    pattern_data = db.Column(JSON)
    significance_score = db.Column(db.Float)
    recognition_params = db.Column(JSON)
    actions_suggested = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    user = relationship('User', back_populates='spending_patterns')

class CryptoWallet(db.Model):
    __tablename__ = 'crypto_wallets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wallet_address = db.Column(db.String(255), nullable=False)
    blockchain_type = db.Column(db.String(50), nullable=False)
    balance_snapshot = db.Column(JSON)
    transaction_history = db.Column(JSON)
    risk_assessment = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    user = relationship('User', back_populates='crypto_wallets')

class SmartBudget(db.Model):
    __tablename__ = 'smart_budgets'

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    ai_parameters = db.Column(JSON)
    market_conditions = db.Column(JSON)
    adjustment_history = db.Column(JSON)
    performance_metrics = db.Column(JSON)
    suggestion_log = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    budget = relationship('Budget', back_populates='smart_budget')

class FinancialBenchmark(db.Model):
    __tablename__ = 'financial_benchmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    peer_group_params = db.Column(JSON)
    comparison_metrics = db.Column(JSON)
    insights_generated = db.Column(JSON)
    recommendation_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    user = relationship('User', back_populates='financial_benchmarks')

class XRVisualization(db.Model):
    __tablename__ = 'xr_visualizations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visualization_type = db.Column(Enum('ar_overlay', 'vr_space', 'mixed_reality', name='xr_visualization_type'))
    scene_data = db.Column(JSON)
    interaction_metrics = db.Column(JSON)
    performance_stats = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    user = relationship('User', back_populates='xr_visualizations')
