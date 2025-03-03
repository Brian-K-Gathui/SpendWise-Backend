from server.models import db, CryptoWallet

def get_all_crypto_wallets():
    wallets = [cw.serialize() for cw in CryptoWallet.query.all()]
    return wallets, 200

def get_crypto_wallet_by_id(wallet_id):
    cw = CryptoWallet.query.get(wallet_id)
    if not cw:
        return {"error": "Crypto Wallet not found"}, 404
    return cw.serialize(), 200

def create_crypto_wallet(data):
    required_fields = ['user_id', 'wallet_address']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_cw = CryptoWallet(
        user_id=data.get('user_id'),
        wallet_address=data.get('wallet_address'),
        blockchain_type=data.get('blockchain_type'),
        balance_snapshot=data.get('balance_snapshot'),
        transaction_history=data.get('transaction_history'),
        risk_assessment=data.get('risk_assessment')
    )
    db.session.add(new_cw)
    db.session.commit()
    return new_cw.serialize(), 201

def update_crypto_wallet(wallet_id, data):
    cw = CryptoWallet.query.get(wallet_id)
    if not cw:
        return {"error": "Crypto Wallet not found"}, 404
    for key, value in data.items():
        setattr(cw, key, value)
    db.session.commit()
    return cw.serialize(), 200

def delete_crypto_wallet(wallet_id):
    cw = CryptoWallet.query.get(wallet_id)
    if not cw:
        return {"error": "Crypto Wallet not found"}, 404
    db.session.delete(cw)
    db.session.commit()
    return {"message": "Crypto Wallet deleted successfully"}, 200
