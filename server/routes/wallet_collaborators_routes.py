from flask import request
from flask_restful import Resource
from server.controllers.wallet_collaborators_controller import (
    get_collaborators_for_wallet,
    get_wallet_collaborator_by_id,
    add_collaborator,
    update_collaborator,
    delete_collaborator
)

class WalletCollaboratorsResource(Resource):
    def get(self, wallet_id):
        collaborators, status_code = get_collaborators_for_wallet(wallet_id)
        return collaborators, status_code

    def post(self, wallet_id):
        data = request.get_json()
        collaborator, status_code = add_collaborator(wallet_id, data)
        return collaborator, status_code

class WalletCollaboratorByIdResource(Resource):
    def get(self, wallet_id, collaborator_id):
        collaborator, status_code = get_wallet_collaborator_by_id(wallet_id, collaborator_id)
        return collaborator, status_code

    def patch(self, wallet_id, collaborator_id):
        data = request.get_json()
        collaborator, status_code = update_collaborator(wallet_id, collaborator_id, data)
        return collaborator, status_code

    def delete(self, wallet_id, collaborator_id):
        response, status_code = delete_collaborator(wallet_id, collaborator_id)
        return response, status_code
