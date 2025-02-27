# Imports
import os
from flask import jsonify
from flask_restful import Api
from server.config import app, db
from server.routes import register_routes

# Initialize Flask-RESTful API and register routes
api = Api(app)
register_routes(api)

# Serve React frontend
@app.route("/", defaults={"path": ""})

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({"message": "API is running!"}), 200

# Run the Flask app for development
if __name__ == "__main__":
    is_local = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=is_local)
