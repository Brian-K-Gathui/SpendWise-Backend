from flask import request
from flask_restful import Resource
from server.controllers.smart_budget_controller import (
    get_all_smart_budgets,
    get_smart_budget_by_id,
    create_smart_budget,
    update_smart_budget,
    delete_smart_budget
)

class SmartBudgetsResource(Resource):
    def get(self):
        smart_budgets, status_code = get_all_smart_budgets()
        return smart_budgets, status_code

    def post(self):
        data = request.get_json()
        sb, status_code = create_smart_budget(data)
        return sb, status_code

class SmartBudgetByIdResource(Resource):
    def get(self, sb_id):
        sb, status_code = get_smart_budget_by_id(sb_id)
        return sb, status_code

    def patch(self, sb_id):
        data = request.get_json()
        sb, status_code = update_smart_budget(sb_id, data)
        return sb, status_code

    def delete(self, sb_id):
        response, status_code = delete_smart_budget(sb_id)
        return response, status_code
