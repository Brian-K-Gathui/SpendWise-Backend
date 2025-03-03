from flask import request
from flask_restful import Resource
from server.controllers.voice_transaction_controller import (
    get_all_voice_transactions,
    get_voice_transaction_by_id,
    create_voice_transaction,
    update_voice_transaction,
    delete_voice_transaction
)

class VoiceTransactionsResource(Resource):
    def get(self):
        transactions, status_code = get_all_voice_transactions()
        return transactions, status_code

    def post(self):
        data = request.get_json()
        vt, status_code = create_voice_transaction(data)
        return vt, status_code

class VoiceTransactionByIdResource(Resource):
    def get(self, vt_id):
        vt, status_code = get_voice_transaction_by_id(vt_id)
        return vt, status_code

    def patch(self, vt_id):
        data = request.get_json()
        vt, status_code = update_voice_transaction(vt_id, data)
        return vt, status_code

    def delete(self, vt_id):
        response, status_code = delete_voice_transaction(vt_id)
        return response, status_code
