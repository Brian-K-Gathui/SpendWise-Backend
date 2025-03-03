from flask import request
from flask_restful import Resource
from server.controllers.financial_benchmark_controller import (
    get_all_financial_benchmarks,
    get_financial_benchmark_by_id,
    create_financial_benchmark,
    update_financial_benchmark,
    delete_financial_benchmark
)

class FinancialBenchmarksResource(Resource):
    def get(self):
        benchmarks, status_code = get_all_financial_benchmarks()
        return benchmarks, status_code

    def post(self):
        data = request.get_json()
        fb, status_code = create_financial_benchmark(data)
        return fb, status_code

class FinancialBenchmarkByIdResource(Resource):
    def get(self, benchmark_id):
        fb, status_code = get_financial_benchmark_by_id(benchmark_id)
        return fb, status_code

    def patch(self, benchmark_id):
        data = request.get_json()
        fb, status_code = update_financial_benchmark(benchmark_id, data)
        return fb, status_code

    def delete(self, benchmark_id):
        response, status_code = delete_financial_benchmark(benchmark_id)
        return response, status_code
