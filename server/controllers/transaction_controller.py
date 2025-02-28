from datetime import datetime
from server.models import db, Transaction

def get_all_transactions():
    transactions = [transaction.serialize() for transaction in Transaction.query.all()]
    return transactions, 200

def get_transaction_by_id(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return {"error": "Transaction not found"}, 404
    return transaction.serialize(), 200

def create_transaction(data):
    required_fields = ['wallet_id', 'category_id', 'amount', 'type', 'date', 'created_by']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    try:
        # Expecting ISO format date string
        date = datetime.fromisoformat(data.get('date'))
    except Exception:
        return {"error": "Invalid date format. Please use ISO format."}, 400

    new_transaction = Transaction(
        wallet_id=data.get('wallet_id'),
        category_id=data.get('category_id'),
        amount=data.get('amount'),
        type=data.get('type'),
        description=data.get('description'),
        date=date,
        is_recurring=data.get('is_recurring', False),
        recurring_interval=data.get('recurring_interval'),
        created_by=data.get('created_by')
    )

    db.session.add(new_transaction)
    db.session.commit()
    return new_transaction.serialize(), 201

def update_transaction(transaction_id, data):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return {"error": "Transaction not found"}, 404

    allowed_fields = {'wallet_id', 'category_id', 'amount', 'type', 'description', 'date', 'is_recurring', 'recurring_interval'}
    for key, value in data.items():
        if key in allowed_fields:
            if key == 'date':
                try:
                    value = datetime.fromisoformat(value)
                except Exception:
                    return {"error": "Invalid date format. Please use ISO format."}, 400
            setattr(transaction, key, value)
    db.session.commit()
    return transaction.serialize(), 200

def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return {"error": "Transaction not found"}, 404
    db.session.delete(transaction)
    db.session.commit()
    return {"message": "Transaction deleted successfully"}, 200
