import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from app import app
from models import db, Category

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def seed_categories():
    """Seed default categories"""
    with app.app_context():
        # Define default categories with icons and colors
        default_categories = [
            {
                'name': 'Food & Dining',
                'description': 'Restaurants, groceries, and food delivery',
                'icon': 'utensils',
                'color': '#EF4444',  # Red
                'type': 'income'
            },
            {
                'name': 'Transportation',
                'description': 'Public transit, gas, car maintenance',
                'icon': 'car',
                'color': '#F59E0B',  # Amber
                'type': 'expense'
            },
            {
                'name': 'Housing',
                'description': 'Rent, mortgage, utilities',
                'icon': 'home',
                'color': '#10B981',  # Emerald
                'type': 'expense'
            },
            {
                'name': 'Entertainment',
                'description': 'Movies, games, streaming services',
                'icon': 'film',
                'color': '#3B82F6',  # Blue
                'type': 'expense'
            },
            {
                'name': 'Shopping',
                'description': 'Clothing, electronics, personal items',
                'icon': 'shopping-bag',
                'color': '#8B5CF6',  # Violet
                'type': 'income'
            },
            {
                'name': 'Health',
                'description': 'Medical expenses, pharmacy, fitness',
                'icon': 'heart-pulse',
                'color': '#EC4899',  # Pink
                'type': 'expense'
            },
            {
                'name': 'Education',
                'description': 'Tuition, books, courses',
                'icon': 'book',
                'color': '#F97316',  # Orange
                'type': 'income'
            },
            {
                'name': 'Travel',
                'description': 'Flights, hotels, vacations',
                'icon': 'plane',
                'color': '#06B6D4',  # Cyan
                'type': 'expense'
            },
            {
                'name': 'Income',
                'description': 'Salary, investments, gifts received',
                'icon': 'wallet',
                'color': '#22C55E',  # Green
                'type': 'income'
            },
            {
                'name': 'Other',
                'description': 'Miscellaneous expenses',
                'icon': 'more-horizontal',
                'color': '#6B7280',  # Gray
                'type': 'expense'
            }
        ]

        # Check if categories already exist
        existing_categories = Category.query.all()
        if existing_categories:
            logger.info(f"Found {len(existing_categories)} existing categories. Skipping seed.")
            return

        # Create categories
        for category_data in default_categories:
            category = Category(
                name=category_data['name'],
                description=category_data['description'],
                icon=category_data['icon'],
                color=category_data['color'],
                type=category_data['type']  # Added the required type field
            )
            db.session.add(category)

        # Commit changes
        db.session.commit()
        logger.info(f"Created {len(default_categories)} default categories")

if __name__ == "__main__":
    seed_categories()
