from flask_restful import Resource, reqparse
from flask import g, request, jsonify
from models import db, User
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from supabase import create_client
import os

logger = logging.getLogger(__name__)

class SupabaseResource(Resource):
    def post(self):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return jsonify({'error': 'User ID not found in token'}), 400

            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('data', type=dict, required=True, help='User data is required')
            args = parser.parse_args()

            # Initialize Supabase client
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            supabase = create_client(supabase_url, supabase_key)

            # Use RPC function to handle upsert
            response = supabase.rpc(
                'insert_or_update_user_data',
                {
                    'p_user_id': user_id,
                    'p_email': args['data'].get('email', ''),
                    'p_data': args['data']
                }
            ).execute()

            if response.get('error'):
                return jsonify({'error': 'Failed to sync with Supabase', 'details': response.get('error')}), 500

            return jsonify({'message': 'User data synced with Supabase successfully'})

        except Exception as e:
            logger.error(f"Error in POST /api/supabase/sync: {str(e)}")
            return jsonify({'error': str(e)}), 500
