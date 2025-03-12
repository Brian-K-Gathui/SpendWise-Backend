import os
from supabase import create_client
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase = create_client(self.supabase_url, self.supabase_key)

    def get_user_data(self, user_id):
        try:
            response = self.supabase.table('user_data').select('*').eq('user_id', user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user data from Supabase: {str(e)}")
            return None

    def create_or_update_user(self, user_id, email, data=None):
        if data is None:
            data = {}

        try:
            # Call the RPC function to insert or update user data
            response = self.supabase.rpc(
                'insert_or_update_user_data',
                {
                    'p_user_id': user_id,
                    'p_email': email,
                    'p_data': data
                }
            ).execute()

            return response.data
        except Exception as e:
            logger.error(f"Error creating/updating user in Supabase: {str(e)}")
            return None
