from flask import Flask, jsonify, g, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
import os
from datetime import datetime
import json
from models import db, User
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from supabase import create_client
from functools import wraps
import jwt
from resources.userResource import UserResource
from resources.walletResource import WalletResource
from resources.transactionResource import TransactionResource
from resources.budgetResource import BudgetResource
from resources.categoryResource import CategoryResource
from resources.notificationResource import NotificationResource
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from services.supabase_service import SupabaseService

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Flask instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,  # Start with 5 connections
    'max_overflow': 10,  # Allow up to 10 more connections
    'pool_timeout': 30,  # Timeout after 30 seconds
    'pool_recycle': 1800,  # Recycle connections after 30 minutes
    'pool_pre_ping': True,  # Check connection validity before using it
}

# Enable CORS - Updated to fix preflight issues
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 86400  # Cache preflight response for 24 hours
    }
})

# Custom JSON encoder for datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Setup Flask-RESTful with custom JSON encoder
api = Api(app)
# Apply the custom encoder to Flask-RESTful
app.config['RESTFUL_JSON'] = {'cls': CustomJSONEncoder}

# Create Migrate object
migrate = Migrate(app, db)

# Initialize the database
db.init_app(app)

# Setup rate limiting with exemptions for OPTIONS requests
def rate_limit_key_func():
    # Skip rate limiting for OPTIONS requests
    if request.method == 'OPTIONS':
        return None  # Return None to skip rate limiting
    return get_remote_address()

limiter = Limiter(
    app=app,
    key_func=rate_limit_key_func,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Exempt OPTIONS requests from rate limiting
@limiter.exempt
@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path=None):
    return '', 200

# Initialize Supabase service
supabase_service = SupabaseService()

def verify_clerk_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {"error": "No token provided"}, 401

        token = auth_header.split(' ')[1]
        try:
            # Verify the token signature if you have the Clerk public key
            # For simplicity, we're just decoding without verification here
            # In production, you should verify the token signature
            decoded = jwt.decode(token, options={"verify_signature": False})
            g.user = decoded
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401
    return decorated_function

# Apply the verify_clerk_token decorator to all routes
@app.before_request
def before_request():
    # Skip authentication for OPTIONS requests (CORS preflight)
    if request.method == 'OPTIONS':
        return

    # Skip authentication for the home route
    if request.path == '/':
        return

    # Apply token verification
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {"error": "No token provided"}, 401

    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        g.user = decoded
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"An error occurred: {str(error)}")
    response_data = {"error": str(error), "message": "An internal server error occurred"}
    return response_data, 500

@app.route('/')
def home():
    return {"message": "Welcome to the SpendWise API"}, 200

# Add resources to the API
api.add_resource(UserResource, '/api/users', '/api/users/<string:user_id>')
api.add_resource(WalletResource, '/api/wallets', '/api/wallets/<int:wallet_id>')
api.add_resource(TransactionResource, '/api/transactions', '/api/transactions/<int:transaction_id>')
api.add_resource(BudgetResource, '/api/budgets', '/api/budgets/<int:budget_id>')
api.add_resource(CategoryResource, '/api/categories', '/api/categories/<int:category_id>')
api.add_resource(NotificationResource, '/api/notifications', '/api/notifications/<int:notification_id>')

@app.errorhandler(404)
def not_found(error):
    return {"error": "Not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500

# Handle 429 Too Many Requests errors
@app.errorhandler(429)
def ratelimit_handler(error):
    return {"error": "Rate limit exceeded. Please try again later."}, 429

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)
