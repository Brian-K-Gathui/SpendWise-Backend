from flask import Flask, jsonify, g, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
import os
from datetime import datetime
import json
from models import db,User
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from supabase import create_client
from functools import wraps
import jwt
from flask import Response
from resources.userResource import UserResource
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

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

# Enable CORS
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

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

    # Skip authentication for the home route
    if request.path == '/':
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

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"An error occurred: {str(error)}")
    response_data = {"error": str(error), "message": "An internal server error occurred"}
    return Response(json.dumps(response_data, cls=CustomJSONEncoder), status=500, mimetype="application/json")

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the API"}), 200

# Add the UserResource to the API
api.add_resource(UserResource, '/users', '/users/<string:user_id>')

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(port=5000, debug=True)
