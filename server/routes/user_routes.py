from flask import request
from flask_restful import Resource
from server.controllers.user_controller import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user
)

class UserResource(Resource):
    def get(self):
        users, status_code = get_all_users()
        return users, status_code

    def post(self):
        data = request.get_json()
        user, status_code = create_user(data)
        return user, status_code

class UserByIdResource(Resource):
    def get(self, user_id):
        user, status_code = get_user_by_id(user_id)
        return user, status_code

    def patch(self, user_id):
        data = request.get_json()
        user, status_code = update_user(user_id, data)
        return user, status_code

    def delete(self, user_id):
        response, status_code = delete_user(user_id)
        return response, status_code
