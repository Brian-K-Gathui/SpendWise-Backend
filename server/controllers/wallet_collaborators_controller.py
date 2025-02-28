from server.models import db, WalletCollaborator

def get_collaborators_for_wallet(wallet_id):
    collaborators = WalletCollaborator.query.filter_by(wallet_id=wallet_id).all()
    collaborators_serialized = [collaborator.serialize() for collaborator in collaborators]
    return collaborators_serialized, 200

def get_wallet_collaborator_by_id(wallet_id, collaborator_id):
    collaborator = WalletCollaborator.query.filter_by(wallet_id=wallet_id, id=collaborator_id).first()
    if not collaborator:
        return {"error": "Collaborator not found"}, 404
    return collaborator.serialize(), 200

def add_collaborator(wallet_id, data):
    required_fields = ['user_id', 'permission_level']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    new_collaborator = WalletCollaborator(
        wallet_id=wallet_id,
        user_id=data.get('user_id'),
        permission_level=data.get('permission_level')
    )

    db.session.add(new_collaborator)
    db.session.commit()
    return new_collaborator.serialize(), 201

def update_collaborator(wallet_id, collaborator_id, data):
    collaborator = WalletCollaborator.query.filter_by(wallet_id=wallet_id, id=collaborator_id).first()
    if not collaborator:
        return {"error": "Collaborator not found"}, 404

    allowed_fields = {'permission_level'}
    for key, value in data.items():
        if key in allowed_fields:
            setattr(collaborator, key, value)
    db.session.commit()
    return collaborator.serialize(), 200

def delete_collaborator(wallet_id, collaborator_id):
    collaborator = WalletCollaborator.query.filter_by(wallet_id=wallet_id, id=collaborator_id).first()
    if not collaborator:
        return {"error": "Collaborator not found"}, 404
    db.session.delete(collaborator)
    db.session.commit()
    return {"message": "Collaborator deleted successfully"}, 200
