import os
from flask import jsonify
from flask_restful import Api
from server.config import app, db
from server.models import User
from server.routes import register_routes

# Initialize Flask-RESTful API and register routes
api = Api(app)
register_routes(api)

# Serve React frontend or landing page
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    return jsonify({
        "message": "Welcome to SpendWise API",
        "endpoints": {
            "health": "/api/health"
        }
    }), 200

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({"message": "API is running!"}), 200

# Run the Flask app for development
if __name__ == "__main__":
    is_local = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=is_local)
