from flask import request
from flask_restful import Resource
from server.controllers.financial_forecast_controller import (
    get_all_financial_forecasts,
    get_financial_forecast_by_id,
    create_financial_forecast,
    update_financial_forecast,
    delete_financial_forecast
)

class FinancialForecastsResource(Resource):
    def get(self):
        forecasts, status_code = get_all_financial_forecasts()
        return forecasts, status_code

    def post(self):
        data = request.get_json()
        ff, status_code = create_financial_forecast(data)
        return ff, status_code

class FinancialForecastByIdResource(Resource):
    def get(self, forecast_id):
        ff, status_code = get_financial_forecast_by_id(forecast_id)
        return ff, status_code

    def patch(self, forecast_id):
        data = request.get_json()
        ff, status_code = update_financial_forecast(forecast_id, data)
        return ff, status_code

    def delete(self, forecast_id):
        response, status_code = delete_financial_forecast(forecast_id)
        return response, status_code
