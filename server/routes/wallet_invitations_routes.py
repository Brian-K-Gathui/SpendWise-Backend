from flask import request
from flask_restful import Resource
from server.controllers.wallet_invitation_controller import (
    get_all_wallet_invitations,
    get_wallet_invitation_by_id,
    create_wallet_invitation,
    update_wallet_invitation,
    delete_wallet_invitation
)

class WalletInvitationsResource(Resource):
    def get(self):
        invitations, status_code = get_all_wallet_invitations()
        return invitations, status_code

    def post(self):
        data = request.get_json()
        inv, status_code = create_wallet_invitation(data)
        return inv, status_code

class WalletInvitationByIdResource(Resource):
    def get(self, invitation_id):
        inv, status_code = get_wallet_invitation_by_id(invitation_id)
        return inv, status_code

    def patch(self, invitation_id):
        data = request.get_json()
        inv, status_code = update_wallet_invitation(invitation_id, data)
        return inv, status_code

    def delete(self, invitation_id):
        response, status_code = delete_wallet_invitation(invitation_id)
        return response, status_code
