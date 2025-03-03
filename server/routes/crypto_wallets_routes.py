from flask import request
from flask_restful import Resource
from server.controllers.crypto_wallet_controller import (
    get_all_crypto_wallets,
    get_crypto_wallet_by_id,
    create_crypto_wallet,
    update_crypto_wallet,
    delete_crypto_wallet
)

class CryptoWalletsResource(Resource):
    def get(self):
        wallets, status_code = get_all_crypto_wallets()
        return wallets, status_code

    def post(self):
        data = request.get_json()
        cw, status_code = create_crypto_wallet(data)
        return cw, status_code

class CryptoWalletByIdResource(Resource):
    def get(self, wallet_id):
        cw, status_code = get_crypto_wallet_by_id(wallet_id)
        return cw, status_code

    def patch(self, wallet_id):
        data = request.get_json()
        cw, status_code = update_crypto_wallet(wallet_id, data)
        return cw, status_code

    def delete(self, wallet_id):
        response, status_code = delete_crypto_wallet(wallet_id)
        return response, status_code
