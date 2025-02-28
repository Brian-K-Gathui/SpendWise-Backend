from server.models import db, Wallet

def get_all_wallets():
    wallets = [wallet.serialize() for wallet in Wallet.query.all()]
    return wallets, 200

def get_wallet_by_id(wallet_id):
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        return {"error": "Wallet not found"}, 404
    return wallet.serialize(), 200

def create_wallet(data):
    required_fields = ['name', 'owner_id']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    new_wallet = Wallet(
        name=data.get('name'),
        description=data.get('description'),
        currency=data.get('currency', 'KES'),
        balance=data.get('balance', 0),
        type=data.get('type'),
        owner_id=data.get('owner_id')
    )

    db.session.add(new_wallet)
    db.session.commit()
    return new_wallet.serialize(), 201

def update_wallet(wallet_id, data):
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        return {"error": "Wallet not found"}, 404

    allowed_fields = {'name', 'description', 'currency', 'balance', 'type'}
    for key, value in data.items():
        if key in allowed_fields:
            setattr(wallet, key, value)
    db.session.commit()
    return wallet.serialize(), 200

def delete_wallet(wallet_id):
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        return {"error": "Wallet not found"}, 404
    db.session.delete(wallet)
    db.session.commit()
    return {"message": "Wallet deleted successfully"}, 200
