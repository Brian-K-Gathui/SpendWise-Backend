import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import the app and models
from app import app
from models import db, Category

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def seed_categories():
    """Seed default categories"""
    with app.app_context():
        # Define default categories with emojis and colors
        default_categories = [
            # Expense categories
            {
                'name': 'Food & Dining',
                'type': 'expense',
                'description': 'Restaurants, groceries, and food delivery',
                'icon': '🍔',
                'color': '#FF5252'
            },
            {
                'name': 'Transportation',
                'type': 'expense',
                'description': 'Gas, public transit, rideshares, and vehicle maintenance',
                'icon': '🚗',
                'color': '#448AFF'
            },
            {
                'name': 'Housing',
                'type': 'expense',
                'description': 'Rent, mortgage, and home repairs',
                'icon': '🏠',
                'color': '#7C4DFF'
            },
            {
                'name': 'Utilities',
                'type': 'expense',
                'description': 'Electricity, water, internet, and phone bills',
                'icon': '💡',
                'color': '#FFD740'
            },
            {
                'name': 'Entertainment',
                'type': 'expense',
                'description': 'Movies, concerts, subscriptions, and hobbies',
                'icon': '🎬',
                'color': '#FF6E40'
            },
            {
                'name': 'Shopping',
                'type': 'expense',
                'description': 'Clothing, electronics, and personal items',
                'icon': '🛍️',
                'color': '#EC407A'
            },
            {
                'name': 'Health & Medical',
                'type': 'expense',
                'description': 'Doctor visits, medications, and health insurance',
                'icon': '🏥',
                'color': '#26A69A'
            },
            {
                'name': 'Education',
                'type': 'expense',
                'description': 'Tuition, books, and courses',
                'icon': '📚',
                'color': '#5C6BC0'
            },
            {
                'name': 'Travel',
                'type': 'expense',
                'description': 'Flights, hotels, and vacation expenses',
                'icon': '✈️',
                'color': '#00BCD4'
            },
            {
                'name': 'Other Expenses',
                'type': 'expense',
                'description': 'Miscellaneous expenses',
                'icon': '📝',
                'color': '#78909C'
            },

            # Income categories
            {
                'name': 'Salary',
                'type': 'income',
                'description': 'Regular employment income',
                'icon': '💰',
                'color': '#66BB6A'
            },
            {
                'name': 'Freelance',
                'type': 'income',
                'description': 'Independent contractor work',
                'icon': '💻',
                'color': '#42A5F5'
            },
            {
                'name': 'Investment',
                'type': 'income',
                'description': 'Dividends, interest, and capital gains',
                'icon': '📈',
                'color': '#26C6DA'
            },
            {
                'name': 'Gift',
                'type': 'income',
                'description': 'Money received as gifts',
                'icon': '🎁',
                'color': '#AB47BC'
            },
            {
                'name': 'Refund',
                'type': 'income',
                'description': 'Returned purchases and tax refunds',
                'icon': '↩️',
                'color': '#8D6E63'
            },
            {
                'name': 'Other Income',
                'type': 'income',
                'description': 'Miscellaneous income sources',
                'icon': '📝',
                'color': '#78909C'
            }
        ]

        # Check for existing categories
        existing_categories = Category.query.all()
        existing_count = len(existing_categories)

        if existing_count > 0:
            logger.info(f"Found {existing_count} existing categories.")

            # Check which categories need to be added
            existing_names = {(c.name, c.type) for c in existing_categories}
            categories_to_add = [c for c in default_categories
                               if (c['name'], c['type']) not in existing_names]

            if not categories_to_add:
                logger.info("All default categories already exist. Skipping seed.")
                return

            logger.info(f"Adding {len(categories_to_add)} new categories.")
            default_categories = categories_to_add
        else:
            logger.info("No existing categories found. Creating all defaults.")

        # Create categories
        for category_data in default_categories:
            category = Category(
                name=category_data['name'],
                type=category_data['type'],
                description=category_data['description'],
                icon=category_data['icon'],
                color=category_data['color'],
                created_at=datetime.utcnow()
            )
            db.session.add(category)
            logger.info(f"Added category: {category_data['name']} ({category_data['type']})")

        # Commit changes
        db.session.commit()
        logger.info(f"Successfully created {len(default_categories)} categories")

if __name__ == "__main__":
    seed_categories()
