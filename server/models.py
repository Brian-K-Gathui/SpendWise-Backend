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


# ------------------------------
# AI Advisor Profile Model
# ------------------------------
"""
    AI Advisor Profile Model: Stores AI-powered financial advice preferences and settings.

    Attributes:
    - id: Unique identifier for the AI advisor profile.
    - user_id: Reference to the associated user.
    - risk_tolerance: User's calculated risk tolerance on a scale from 0 to 1.
    - financial_goals: JSON structured data of user's financial objectives.
    - investment_preferences: JSON data of user's investment style preferences.
    - learning_parameters: JSON data for AI model parameters tuned to user behavior.
    - created_at: Timestamp when the profile was created.
    - updated_at: Timestamp when the profile was last updated.
"""
class AIAdvisorProfile(db.Model, SerializerMixin):
    __tablename__ = 'ai_advisor_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    risk_tolerance = db.Column(db.Float, nullable=False)
    financial_goals = db.Column(db.JSON)
    investment_preferences = db.Column(db.JSON)
    learning_parameters = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())


# ------------------------------
# Voice Transaction Model
# ------------------------------
"""
    Voice Transaction Model: Processes voice commands for transaction creation.

    Attributes:
    - id: Unique identifier for the voice transaction.
    - user_id: Reference to the user who made the voice command.
    - audio_url: URL to the stored audio file.
    - transcription: Processed text of the voice command.
    - intent_analysis: JSON data of the detected user intent.
    - extracted_data: JSON data of structured data from voice command.
    - confidence_score: NLP confidence score.
    - status: Status of processing (processing, completed, failed).
    - created_at: Timestamp when the voice transaction was created.
    - processed_at: Timestamp when the voice transaction was processed.
"""
class VoiceTransaction(db.Model, SerializerMixin):
    __tablename__ = 'voice_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    audio_url = db.Column(db.String(255))
    transcription = db.Column(db.Text)
    intent_analysis = db.Column(db.JSON)
    extracted_data = db.Column(db.JSON)
    confidence_score = db.Column(db.Float)
    status = db.Column(db.String(50))  # processing, completed, failed
    created_at = db.Column(db.DateTime, server_default=func.now())
    processed_at = db.Column(db.DateTime)


# ------------------------------
# Spending Pattern Model
# ------------------------------
"""
    Spending Pattern Model: Stores AI-detected financial behavior patterns.

    Attributes:
    - id: Unique identifier for the spending pattern.
    - user_id: Reference to the associated user.
    - pattern_type: Type of pattern (habit, anomaly, opportunity).
    - pattern_data: JSON data with details of the detected pattern.
    - significance_score: A score indicating the importance of the pattern.
    - recognition_params: JSON parameters used for pattern recognition.
    - actions_suggested: JSON data with AI-suggested actions.
    - created_at: Timestamp when the pattern was created.
    - updated_at: Timestamp when the pattern was last updated.
"""
class SpendingPattern(db.Model, SerializerMixin):
    __tablename__ = 'spending_patterns'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pattern_type = db.Column(db.String(50))
    pattern_data = db.Column(db.JSON)
    significance_score = db.Column(db.Float)
    recognition_params = db.Column(db.JSON)
    actions_suggested = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())


# ------------------------------
# Financial Benchmark Model
# ------------------------------
"""
    Financial Benchmark Model: Stores peer comparison and financial performance metrics.

    Attributes:
    - id: Unique identifier for the financial benchmark.
    - user_id: Reference to the associated user.
    - peer_group_params: JSON data defining the anonymized peer group.
    - comparison_metrics: JSON data with comparative financial metrics.
    - insights_generated: JSON data with AI-generated insights.
    - recommendation_score: Score representing peer recommendation rating.
    - created_at: Timestamp when the benchmark was created.
    - updated_at: Timestamp when the benchmark was last updated.
"""
class FinancialBenchmark(db.Model, SerializerMixin):
    __tablename__ = 'financial_benchmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    peer_group_params = db.Column(db.JSON)
    comparison_metrics = db.Column(db.JSON)
    insights_generated = db.Column(db.JSON)
    recommendation_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())


# ------------------------------
# XR Visualization Model
# ------------------------------
"""
    XR Visualization Model: Stores AR/VR financial data visualization settings.

    Attributes:
    - id: Unique identifier for the XR visualization.
    - user_id: Reference to the associated user.
    - visualization_type: Type of visualization (ar_overlay, vr_space, mixed_reality).
    - scene_data: JSON data with 3D scene configuration.
    - interaction_metrics: JSON data with user interaction metrics.
    - performance_stats: JSON data with rendering performance statistics.
    - created_at: Timestamp when the visualization was created.
    - updated_at: Timestamp when the visualization was last updated.
"""
class XRVisualization(db.Model, SerializerMixin):
    __tablename__ = 'xr_visualizations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visualization_type = db.Column(db.String(50))
    scene_data = db.Column(db.JSON)
    interaction_metrics = db.Column(db.JSON)
    performance_stats = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())


# ------------------------------
# Crypto Wallet Model
# ------------------------------
"""
    Crypto Wallet Model: Manages cryptocurrency wallet integration and tracking.

    Attributes:
    - id: Unique identifier for the crypto wallet.
    - user_id: Reference to the associated user.
    - wallet_address: Blockchain wallet address.
    - blockchain_type: Type of blockchain.
    - balance_snapshot: JSON data with the latest balance snapshot.
    - transaction_history: JSON data with recent transaction history.
    - risk_assessment: JSON data with AI-generated risk metrics.
    - created_at: Timestamp when the crypto wallet was created.
    - updated_at: Timestamp when the crypto wallet was last updated.
"""
class CryptoWallet(db.Model, SerializerMixin):
    __tablename__ = 'crypto_wallets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wallet_address = db.Column(db.String(255))
    blockchain_type = db.Column(db.String(50))
    balance_snapshot = db.Column(db.JSON)
    transaction_history = db.Column(db.JSON)
    risk_assessment = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())


# ------------------------------
# Financial Forecast Model
# ------------------------------
"""
    Financial Forecast Model: Stores ML-based financial predictions and analysis.

    Attributes:
    - id: Unique identifier for the forecast.
    - user_id: Reference to the associated user.
    - wallet_id: Reference to the target wallet.
    - forecast_type: Type of forecast (spending, income, savings, investment).
    - time_range: Time range for the forecast (weekly, monthly, quarterly, yearly).
    - prediction_data: JSON data with the forecast predictions.
    - confidence_interval: JSON data with statistical confidence intervals.
    - model_version: Version of the ML model used.
    - accuracy_metrics: JSON data with model performance metrics.
    - created_at: Timestamp when the forecast was created.
    - valid_until: Timestamp indicating forecast validity.
"""
class FinancialForecast(db.Model, SerializerMixin):
    __tablename__ = 'financial_forecasts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    forecast_type = db.Column(db.String(50))
    time_range = db.Column(db.String(50))
    prediction_data = db.Column(db.JSON)
    confidence_interval = db.Column(db.JSON)
    model_version = db.Column(db.String(50))
    accuracy_metrics = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=func.now())
    valid_until = db.Column(db.DateTime)


# ------------------------------
# Smart Category Model
# ------------------------------
"""
    Smart Category Model: AI-enhanced dynamic categorization system.

    Attributes:
    - id: Unique identifier for the smart category.
    - name: Dynamic category name.
    - parent_category_id: Reference to the standard category.
    - rules_set: JSON data with ML-based categorization rules.
    - learning_threshold: Sensitivity parameter for adaptation.
    - confidence_minimum: Minimum confidence required for auto-categorization.
    - created_at: Timestamp when the smart category was created.
    - updated_at: Timestamp when the smart category was last updated.
"""
class SmartCategory(db.Model, SerializerMixin):
    __tablename__ = 'smart_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    rules_set = db.Column(db.JSON)
    learning_threshold = db.Column(db.Float)
    confidence_minimum = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())


# ------------------------------
# Wallet Invitation Model
# ------------------------------
"""
    Wallet Invitation Model: Manages wallet sharing invitations.

    Attributes:
    - id: Unique identifier for the invitation.
    - wallet_id: Reference to the wallet being shared.
    - invited_by: Reference to the user sending the invitation.
    - invited_email: Email address of the invitee.
    - permission_level: Proposed access level for the invitee.
    - status: Current invitation status (pending, accepted, rejected).
    - created_at: Timestamp when the invitation was sent.
    - expires_at: Timestamp when the invitation expires.
"""
class WalletInvitation(db.Model, SerializerMixin):
    __tablename__ = 'wallet_invitations'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invited_email = db.Column(db.String(120), nullable=False)
    permission_level = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50))  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, server_default=func.now())
    expires_at = db.Column(db.DateTime)


# ------------------------------
# Smart Budget Model
# ------------------------------
"""
    Smart Budget Model: AI-powered budget optimization enhancements.

    Attributes:
    - id: Unique identifier for the smart budget.
    - budget_id: Reference to the standard budget.
    - ai_parameters: JSON data with AI optimization parameters.
    - market_conditions: JSON data with external market data.
    - adjustment_history: JSON data with historical adjustments.
    - performance_metrics: JSON data with budget performance metrics.
    - suggestion_log: JSON data with AI-generated suggestions.
    - created_at: Timestamp when the smart budget was created.
    - updated_at: Timestamp when the smart budget was last updated.
"""
class SmartBudget(db.Model, SerializerMixin):
    __tablename__ = 'smart_budgets'
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    ai_parameters = db.Column(db.JSON)
    market_conditions = db.Column(db.JSON)
    adjustment_history = db.Column(db.JSON)
    performance_metrics = db.Column(db.JSON)
    suggestion_log = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())


# ------------------------------
# Notification Model
# ------------------------------
"""
    Notification Model: Handles system notifications for users.

    Attributes:
    - id: Unique identifier for the notification.
    - user_id: Reference to the recipient user.
    - type: Type of notification (budget_alert, shared_wallet_invite, security_alert).
    - title: Short title of the notification.
    - message: Detailed content of the notification.
    - is_read: Boolean flag indicating if the notification has been read.
    - created_at: Timestamp when the notification was generated.
"""
class Notification(db.Model, SerializerMixin):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50))
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

# ====================================
# Receipt Scan Model
# ====================================
"""
    Receipt Scan Model: Manages OCR-processed receipt data and metadata.

    Attributes:
    - id: Unique identifier for each scan.
    - user_id: Reference to the user who submitted the receipt.
    - image_url: URL to the stored receipt image.
    - ocr_text: Extracted text from the receipt.
    - confidence_score: ML confidence in extraction accuracy.
    - merchant_name: Extracted merchant name.
    - purchase_date: Date of purchase.
    - items_detected: JSON data of detected items.
    - total_amount: Total amount extracted.
    - status: Status of processing (processing, completed, failed).
    - created_at: When the receipt was submitted.
    - processed_at: When the receipt was processed.
"""
class ReceiptScan(db.Model, SerializerMixin):
    __tablename__ = 'receipt_scans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255))
    ocr_text = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    merchant_name = db.Column(db.String(255))
    purchase_date = db.Column(db.DateTime)
    items_detected = db.Column(db.JSON)
    total_amount = db.Column(db.Numeric)
    status = db.Column(db.String(50))  # processing, completed, failed
    created_at = db.Column(db.DateTime, server_default=func.now())
    processed_at = db.Column(db.DateTime)
