from flask import request
from flask_restful import Resource
from server.controllers.transaction_controller import (
    get_all_transactions,
    get_transaction_by_id,
    create_transaction,
    update_transaction,
    delete_transaction
)

class TransactionsResource(Resource):
    def get(self):
        transactions, status_code = get_all_transactions()
        return transactions, status_code

    def post(self):
        data = request.get_json()
        transaction, status_code = create_transaction(data)
        return transaction, status_code

class TransactionByIdResource(Resource):
    def get(self, transaction_id):
        transaction, status_code = get_transaction_by_id(transaction_id)
        return transaction, status_code

    def patch(self, transaction_id):
        data = request.get_json()
        transaction, status_code = update_transaction(transaction_id, data)
        return transaction, status_code

    def delete(self, transaction_id):
        response, status_code = delete_transaction(transaction_id)
        return response, status_code
