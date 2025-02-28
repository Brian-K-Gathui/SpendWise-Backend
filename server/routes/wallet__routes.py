from flask import request
from flask_restful import Resource
from server.controllers.wallet__controller import (
    get_all_wallets,
    get_wallet_by_id,
    create_wallet,
    update_wallet,
    delete_wallet
)

class WalletsResource(Resource):
    def get(self):
        wallets, status_code = get_all_wallets()
        return wallets, status_code

    def post(self):
        data = request.get_json()
        wallet, status_code = create_wallet(data)
        return wallet, status_code

class WalletByIdResource(Resource):
    def get(self, wallet_id):
        wallet, status_code = get_wallet_by_id(wallet_id)
        return wallet, status_code

    def patch(self, wallet_id):
        data = request.get_json()
        wallet, status_code = update_wallet(wallet_id, data)
        return wallet, status_code

    def delete(self, wallet_id):
        response, status_code = delete_wallet(wallet_id)
        return response, status_code
