from flask import request
from flask_restful import Resource
from server.controllers.category_controller import (
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category
)

class CategoriesResource(Resource):
    def get(self):
        categories, status_code = get_all_categories()
        return categories, status_code

    def post(self):
        data = request.get_json()
        category, status_code = create_category(data)
        return category, status_code

class CategoryByIdResource(Resource):
    def get(self, category_id):
        category, status_code = get_category_by_id(category_id)
        return category, status_code

    def patch(self, category_id):
        data = request.get_json()
        category, status_code = update_category(category_id, data)
        return category, status_code

    def delete(self, category_id):
        response, status_code = delete_category(category_id)
        return response, status_code
