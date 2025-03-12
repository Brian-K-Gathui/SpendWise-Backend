import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseService:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key must be set in environment variables")

        self.supabase = create_client(self.supabase_url, self.supabase_key)

    def get_user_data(self, user_id):
        """Get user data from Supabase"""
        response = self.supabase.table('user_data').select('*').eq('user_id', user_id).execute()
        return response.data[0] if response.data else None

    def update_user_data(self, user_id, data):
        """Update user data in Supabase"""
        # Check if user exists
        existing_user = self.get_user_data(user_id)

        if existing_user:
            # Update existing user
            response = self.supabase.table('user_data').update({
                'data': data
            }).eq('user_id', user_id).execute()
        else:
            # Create new user
            response = self.supabase.table('user_data').insert({
                'user_id': user_id,
                'data': data
            }).execute()

        return response.data

    def verify_mfa_code(self, user_id, code):
        """Verify MFA code (this would be implemented with your preferred MFA provider)"""
        # This is a placeholder for actual MFA verification logic
        # In a real implementation, you would verify the code with your MFA provider
        # For demo purposes, we'll accept any 6-digit code
        return len(code) == 6 and code.isdigit()

    def send_verification_code(self, user_id, method, destination):
        """Send verification code via email or SMS"""
        # This is a placeholder for actual code sending logic
        # In a real implementation, you would send a code via email or SMS
        # For demo purposes, we'll just return success
        return {'success': True, 'message': f'Verification code sent to {destination}'}

    def reset_password(self, email):
        """Send password reset email"""
        # This is handled by Supabase Auth directly
        # We're just providing a wrapper for consistency
        response = self.supabase.auth.reset_password_for_email(email)
        return response

    def verify_reset_token(self, token):
        """Verify password reset token"""
        # This would be implemented in a real app
        # For demo purposes, we'll just return success
        return {'valid': True}
