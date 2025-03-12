import os
from flask import Flask, jsonify, g, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from supabase import create_client
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
import jwt
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure PostgreSQL from Supabase
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,  # Start with 5 connections
    'max_overflow': 10,  # Allow up to 10 more connections
    'pool_timeout': 30,  # Timeout after 30 seconds
    'pool_recycle': 1800,  # Recycle connections after 30 minutes
    'pool_pre_ping': True,  # Check connection validity before using it
}

# Custom JSON encoder for datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Ensure JSON responses are formatted nicely
app.json.compact = False

# Initialize database and migration tool
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# Setup rate limiting
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

def verify_clerk_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "No token provided"}), 401

        token = auth_header.split(' ')[1]
        try:
            # Verify the token signature if you have the Clerk public key
            # For simplicity, we're just decoding without verification here
            # In production, you should verify the token signature
            decoded = jwt.decode(token, options={"verify_signature": False})
            g.user = decoded
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    return decorated_function

# Apply the verify_clerk_token decorator to all routes
@app.before_request
def before_request():
    # Skip authentication for OPTIONS requests (CORS preflight)
    if request.method == 'OPTIONS':
        return

    # Skip authentication for the home route and health check
    if request.path == '/' or request.path == '/api/health':
        return

    # Apply token verification
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "No token provided"}), 401

    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        g.user = decoded
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

print(f"✅ Flask configured with database: {app.config['SQLALCHEMY_DATABASE_URI']}")
