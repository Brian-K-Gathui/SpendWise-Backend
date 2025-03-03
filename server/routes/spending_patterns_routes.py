from flask import request
from flask_restful import Resource
from server.controllers.spending_pattern_controller import (
    get_all_spending_patterns,
    get_spending_pattern_by_id,
    create_spending_pattern,
    update_spending_pattern,
    delete_spending_pattern
)

class SpendingPatternsResource(Resource):
    def get(self):
        patterns, status_code = get_all_spending_patterns()
        return patterns, status_code

    def post(self):
        data = request.get_json()
        sp, status_code = create_spending_pattern(data)
        return sp, status_code

class SpendingPatternByIdResource(Resource):
    def get(self, pattern_id):
        sp, status_code = get_spending_pattern_by_id(pattern_id)
        return sp, status_code

    def patch(self, pattern_id):
        data = request.get_json()
        sp, status_code = update_spending_pattern(pattern_id, data)
        return sp, status_code

    def delete(self, pattern_id):
        response, status_code = delete_spending_pattern(pattern_id)
        return response, status_code
