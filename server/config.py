import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configure PostgreSQL from Supabase
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres.btianunpjasixtlglmmm:group4-spendwise@aws-0-us-west-1.pooler.supabase.com:6543/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')

# Ensure JSON responses are formatted nicely
app.json.compact = False

# Initialize database and migration tool
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Enable CORS for API endpoints (allowing all origins for development)
CORS(app, resources={r"/api/*": {"origins": "*"}})

print(f"✅ Flask configured with database: {app.config['SQLALCHEMY_DATABASE_URI']}")
