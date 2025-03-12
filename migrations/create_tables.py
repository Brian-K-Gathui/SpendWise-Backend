from app import app, db
from models import User, Wallet, Category, Transaction, Budget, Notification

def create_tables():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()
