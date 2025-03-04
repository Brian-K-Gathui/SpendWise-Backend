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

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Flask instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Enable CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Custom JSON encoder for datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

# Setup Flask-RESTful
api = Api(app)

# Create Migrate object
migrate = Migrate(app, db)

# Initialize the database
db.init_app(app)

# Setup rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

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
            # Verify the JWT token
            # Note: In production, you should fetch the public key from Clerk's JWKS endpoint
            decoded = jwt.decode(
                token,
                options={"verify_signature": False}  # In production, you should verify the signature
            )

            # Add the decoded token to the request context
            g.user = decoded
            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

    return decorated_function

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"An error occurred: {str(error)}")
    return jsonify({
        "error": str(error),
        "message": "An internal server error occurred"
    }), 500

# User routes with rate limiting and Clerk authentication
class UserResource(Resource):
    decorators = [limiter.limit("10 per minute"), verify_clerk_token]

    def get(self, user_id=None):
        try:
            if user_id:
                # Get specific user from Supabase
                response = supabase.from_('users').select('*').eq('clerk_user_id', user_id).execute()
                if not response.data:
                    return {"message": "User not found"}, 404
                return {"user": response.data[0]}, 200

            # Get all users
            response = supabase.from_('users').select('*').execute()
            return {"users": response.data}, 200

        except Exception as e:
            logger.error(f"Error retrieving user(s): {str(e)}")
            return {"message": f"Failed to retrieve user(s): {str(e)}"}, 500

    def post(self):
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['email', 'full_name']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {"message": f"Missing required fields: {', '.join(missing_fields)}"}, 400

            clerk_user_id = g.user.get('sub')

            # Check if user already exists
            existing_user = supabase.from_('users').select('*').eq('clerk_user_id', clerk_user_id).execute()

            user_data = {
                'email': data['email'],
                'full_name': data['full_name'],
                'clerk_user_id': clerk_user_id,
                'updated_at': datetime.utcnow().isoformat()
            }

            if existing_user.data:
                # Update existing user
                response = supabase.from_('users').update(user_data).eq('clerk_user_id', clerk_user_id).execute()
                message = "User updated successfully"
            else:
                # Create new user
                user_data['created_at'] = datetime.utcnow().isoformat()
                response = supabase.from_('users').insert(user_data).execute()
                message = "User created successfully"

            return {
                "message": message,
                "user": response.data[0]
            }, 201

        except Exception as e:
            logger.error(f"Error creating/updating user: {str(e)}")
            return {"message": f"Failed to create/update user: {str(e)}"}, 500

# Add resources to API
api.add_resource(UserResource, '/users', '/users/<string:user_id>')

if __name__ == "__main__":
    with app.app_context():
        # Create all database tables
        db.create_all()
    app.run(port=5000, debug=True)
