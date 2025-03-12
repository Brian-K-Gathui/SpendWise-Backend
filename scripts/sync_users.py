import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from app import app
from models import db, User
from services.supabase_service import SupabaseService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def sync_users():
    """Sync users from Supabase to local database"""
    with app.app_context():
        supabase_service = SupabaseService()

        try:
            # Get all users from Supabase
            response = supabase_service.supabase.table('user_data').select('*').execute()
            supabase_users = response.data

            if not supabase_users:
                logger.info("No users found in Supabase")
                return

            logger.info(f"Found {len(supabase_users)} users in Supabase")

            # Process each user
            for supabase_user in supabase_users:
                user_id = supabase_user['user_id']
                email = supabase_user['email']

                # Check if user exists in local database
                user = User.query.get(user_id)

                if user:
                    # Update existing user
                    user.email = email
                    logger.info(f"Updated user {user_id} in local database")
                else:
                    # Create new user
                    new_user = User(
                        id=user_id,
                        email=email,
                        full_name=supabase_user.get('data', {}).get('full_name', '')
                    )
                    db.session.add(new_user)
                    logger.info(f"Added user {user_id} to local database")

            # Commit changes
            db.session.commit()
            logger.info("User sync completed successfully")

        except Exception as e:
            logger.error(f"Error syncing users: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    sync_users()
