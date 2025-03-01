from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models import db

class BaseResource(Resource):
    method_decorators = [jwt_required()]
    
    def handle_error(self, e):
        db.session.rollback()
        return {'error': str(e)}, 400