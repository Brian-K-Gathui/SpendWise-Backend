from app import app, db
from models import User, Wallet, Category, Transaction, Budget, Notification
from datetime import datetime, timedelta
import random

def seed_database():
    with app.app_context():
        # Clear existing data
        db.session.query(Notification).delete()
        db.session.query(Budget).delete()
        db.session.query(Transaction).delete()
        db.session.query(Wallet).delete()
        db.session.query(Category).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Create default categories
        income_categories = [
            Category(name="Salary", type="income", icon="dollar-sign", color="#27AE60"),
            Category(name="Freelance", type="income", icon="briefcase", color="#2F80ED"),
            Category(name="Investments", type="income", icon="trending-up", color="#9B51E0"),
            Category(name="Gifts", type="income", icon="gift", color="#F2994A"),
            Category(name="Other Income", type="income", icon="plus-circle", color="#828282")
        ]

        expense_categories = [
            Category(name="Food & Dining", type="expense", icon="coffee", color="#EB5757"),
            Category(name="Transportation", type="expense", icon="truck", color="#F2994A"),
            Category(name="Housing", type="expense", icon="home", color="#2F80ED"),
            Category(name="Utilities", type="expense", icon="zap", color="#9B51E0"),
            Category(name="Entertainment", type="expense", icon="film", color="#6FCF97"),
            Category(name="Shopping", type="expense", icon="shopping-bag", color="#F2C94C"),
            Category(name="Health", type="expense", icon="activity", color="#BB6BD9"),
            Category(name="Education", type="expense", icon="book", color="#56CCF2"),
            Category(name="Personal Care", type="expense", icon="user", color="#219653"),
            Category(name="Travel", type="expense", icon="map", color="#F2994A"),
            Category(name="Debt Payments", type="expense", icon="credit-card", color="#EB5757"),
            Category(name="Savings", type="expense", icon="save", color="#2F80ED"),
            Category(name="Gifts & Donations", type="expense", icon="gift", color="#BB6BD9"),
            Category(name="Other Expenses", type="expense", icon="more-horizontal", color="#828282")
        ]

        for category in income_categories + expense_categories:
            db.session.add(category)

        db.session.commit()
        print(f"Created {len(income_categories)} income categories and {len(expense_categories)} expense categories")

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
