from server.models import db, WalletInvitation
from datetime import datetime

def get_all_wallet_invitations():
    invitations = [inv.serialize() for inv in WalletInvitation.query.all()]
    return invitations, 200

def get_wallet_invitation_by_id(invitation_id):
    inv = WalletInvitation.query.get(invitation_id)
    if not inv:
        return {"error": "Wallet Invitation not found"}, 404
    return inv.serialize(), 200

def create_wallet_invitation(data):
    required_fields = ['wallet_id', 'invited_by', 'invited_email', 'permission_level']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_inv = WalletInvitation(
        wallet_id=data.get('wallet_id'),
        invited_by=data.get('invited_by'),
        invited_email=data.get('invited_email'),
        permission_level=data.get('permission_level'),
        status=data.get('status', 'pending')
    )
    if data.get('expires_at'):
        try:
            new_inv.expires_at = datetime.fromisoformat(data.get('expires_at'))
        except Exception:
            return {"error": "Invalid expires_at format. Please use ISO format."}, 400
    db.session.add(new_inv)
    db.session.commit()
    return new_inv.serialize(), 201

def update_wallet_invitation(invitation_id, data):
    inv = WalletInvitation.query.get(invitation_id)
    if not inv:
        return {"error": "Wallet Invitation not found"}, 404
    for key, value in data.items():
        if key == 'expires_at' and value:
            try:
                value = datetime.fromisoformat(value)
            except Exception:
                return {"error": "Invalid expires_at format. Please use ISO format."}, 400
        setattr(inv, key, value)
    db.session.commit()
    return inv.serialize(), 200

def delete_wallet_invitation(invitation_id):
    inv = WalletInvitation.query.get(invitation_id)
    if not inv:
        return {"error": "Wallet Invitation not found"}, 404
    db.session.delete(inv)
    db.session.commit()
    return {"message": "Wallet Invitation deleted successfully"}, 200
