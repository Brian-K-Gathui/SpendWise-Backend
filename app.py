from flask import Flask, jsonify, g
from flask_restful import Api, Resource
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os
from datetime import datetime, timedelta
import json
from models import db
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
from sqlalchemy import func
from supabase import create_client

from resources.user_controller import (
    UserRegistrationResource,
    LoginResource,
    LogoutResource,
    RefreshTokenResource,
    UserResource
)



# Configure logging
logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Flask instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['headers']

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

CORS(app)

# Setup Flask-RESTful
api = Api(app)

# Setup Flask-Bcrypt
bcrypt = Bcrypt(app)

# Setup Flask-JWT-Extended
jwt = JWTManager(app)

# Create Migrate object
migrate = Migrate(app, db)

# Initialize the database
db.init_app(app)

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"An error occurred: {str(error)}")
    return jsonify({
        "error": str(error),
        "message": "An internal server error occurred"
    }), 500

# Add rate limiting to the Flask app
def setup_limiter(app):
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["1 per second"]
    )
    return limiter

# database url and key
url = os.getenv('my_url')
key = os.environ.get('my_key')
supabase = create_client(url, key)
app.supabase = supabase

# Optional Index Resource
class Index(Resource):
    def get(self):
        return {"message": "Welcome to Spendwise API v1"}


# Index route
api.add_resource(Index, '/')

# User routes
api.add_resource(UserRegistrationResource, '/auth/register')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(LogoutResource, '/auth/logout')
api.add_resource(RefreshTokenResource, '/auth/refresh')
api.add_resource(UserResource, '/users', '/users/<int:user_id>')


if __name__ == "__main__":
    app.run(port=5000)
