import os
from flask import jsonify, g, request, Response
from flask_restful import Api
from config import app, db, CustomJSONEncoder
from models import User,Wallet,Transaction,Category,WalletCollaborator,Budget,AIAdvisorProfile,VoiceTransaction,SpendingPattern,FinancialBenchmark,XRVisualization,CryptoWallet,FinancialForecast,WalletInvitation,SmartCategory,ReceiptScan,Notification # Importing all models
from routes import register_routes
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Flask-RESTful API and register routes
api = Api(app)
register_routes(api)

# Serve React frontend or landing page
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    return jsonify({
        "message": "Welcome to SpendWise API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "users": "/api/users",
            "wallets": "/api/wallets",
            "transactions": "/api/transactions",
            "categories": "/api/categories",
            "budgets": "/api/budgets",
            "wallet_invitations": "/api/wallet-invitations"
        }
    }), 200

# Health check endpoint
@app.route('/api/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        db_status = "disconnected"

    return jsonify({
        "status": "healthy",
        "database": db_status,
        "environment": os.getenv("FLASK_ENV", "development")
    }), 200

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"An error occurred: {str(error)}")
    response_data = {"error": str(error), "message": "An internal server error occurred"}
    return Response(json.dumps(response_data, cls=CustomJSONEncoder), status=500, mimetype="application/json")

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": "The requested resource does not exist"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500

# Run the Flask app for development
if __name__ == "__main__":
    is_local = os.getenv("FLASK_ENV", "development") == "development"
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

        # Create default categories if they don't exist
        from models import Category
        default_categories = [
            {"name": "Food & Dining", "type": "expense", "icon": "utensils", "color": "#FF5733", "is_default": True},
            {"name": "Transportation", "type": "expense", "icon": "car", "color": "#33A8FF", "is_default": True},
            {"name": "Housing", "type": "expense", "icon": "home", "color": "#33FF57", "is_default": True},
            {"name": "Entertainment", "type": "expense", "icon": "film", "color": "#D433FF", "is_default": True},
            {"name": "Shopping", "type": "expense", "icon": "shopping-bag", "color": "#FF33A8", "is_default": True},
            {"name": "Utilities", "type": "expense", "icon": "bolt", "color": "#FFD433", "is_default": True},
            {"name": "Healthcare", "type": "expense", "icon": "medkit", "color": "#33FFC4", "is_default": True},
            {"name": "Personal Care", "type": "expense", "icon": "spa", "color": "#FF8333", "is_default": True},
            {"name": "Education", "type": "expense", "icon": "graduation-cap", "color": "#3357FF", "is_default": True},
            {"name": "Gifts & Donations", "type": "expense", "icon": "gift", "color": "#FF33D4", "is_default": True},
            {"name": "Salary", "type": "income", "icon": "money-bill", "color": "#33FF57", "is_default": True},
            {"name": "Bonus", "type": "income", "icon": "award", "color": "#FFD433", "is_default": True},
            {"name": "Investment", "type": "income", "icon": "chart-line", "color": "#33A8FF", "is_default": True},
            {"name": "Freelance", "type": "income", "icon": "laptop", "color": "#D433FF", "is_default": True},
            {"name": "Gifts", "type": "income", "icon": "gift", "color": "#FF33A8", "is_default": True}
        ]

        for category_data in default_categories:
            existing = Category.query.filter_by(name=category_data["name"], is_default=True).first()
            if not existing:
                category = Category(**category_data)
                db.session.add(category)

        db.session.commit()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=is_local)
