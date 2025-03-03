from flask import request
from flask_restful import Resource
from server.controllers.smart_category_controller import (
    get_all_smart_categories,
    get_smart_category_by_id,
    create_smart_category,
    update_smart_category,
    delete_smart_category
)

class SmartCategoriesResource(Resource):
    def get(self):
        smart_categories, status_code = get_all_smart_categories()
        return smart_categories, status_code

    def post(self):
        data = request.get_json()
        sc, status_code = create_smart_category(data)
        return sc, status_code

class SmartCategoryByIdResource(Resource):
    def get(self, sc_id):
        sc, status_code = get_smart_category_by_id(sc_id)
        return sc, status_code

    def patch(self, sc_id):
        data = request.get_json()
        sc, status_code = update_smart_category(sc_id, data)
        return sc, status_code

    def delete(self, sc_id):
        response, status_code = delete_smart_category(sc_id)
        return response, status_code
