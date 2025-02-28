from flask import request
from flask_restful import Resource
from server.controllers.budget_controller import (
    get_all_budgets,
    get_budget_by_id,
    create_budget,
    update_budget,
    delete_budget
)

class BudgetsResource(Resource):
    def get(self):
        budgets, status_code = get_all_budgets()
        return budgets, status_code

    def post(self):
        data = request.get_json()
        budget, status_code = create_budget(data)
        return budget, status_code

class BudgetByIdResource(Resource):
    def get(self, budget_id):
        budget, status_code = get_budget_by_id(budget_id)
        return budget, status_code

    def patch(self, budget_id):
        data = request.get_json()
        budget, status_code = update_budget(budget_id, data)
        return budget, status_code

    def delete(self, budget_id):
        response, status_code = delete_budget(budget_id)
        return response, status_code
