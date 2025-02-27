# Imports
import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app + setting the instance folder to be inside the 'server' directory
app = Flask(__name__, instance_relative_config=True, instance_path=os.path.join(os.path.dirname(__file__), 'instance'))

# Configure the SQLite database for local development
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///spendwise.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')

# Ensure JSON responses are formatted nicely
app.json.compact = False

# Initialize the database and migration tool
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Enable CORS for API endpoints (allowing all origins for development)
CORS(app, resources={r"/api/*": {"origins": "*"}})

print("✅ Flask application configured successfully for development with spendwise.db")
