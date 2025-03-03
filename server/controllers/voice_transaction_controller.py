from server.models import db, VoiceTransaction
from datetime import datetime

def get_all_voice_transactions():
    transactions = [vt.serialize() for vt in VoiceTransaction.query.all()]
    return transactions, 200

def get_voice_transaction_by_id(vt_id):
    vt = VoiceTransaction.query.get(vt_id)
    if not vt:
        return {"error": "Voice Transaction not found"}, 404
    return vt.serialize(), 200

def create_voice_transaction(data):
    required_fields = ['user_id']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_vt = VoiceTransaction(
        user_id=data.get('user_id'),
        audio_url=data.get('audio_url'),
        transcription=data.get('transcription'),
        intent_analysis=data.get('intent_analysis'),
        extracted_data=data.get('extracted_data'),
        confidence_score=data.get('confidence_score'),
        status=data.get('status')
    )
    if data.get('processed_at'):
        try:
            new_vt.processed_at = datetime.fromisoformat(data.get('processed_at'))
        except Exception:
            return {"error": "Invalid processed_at format. Please use ISO format."}, 400
    db.session.add(new_vt)
    db.session.commit()
    return new_vt.serialize(), 201

def update_voice_transaction(vt_id, data):
    vt = VoiceTransaction.query.get(vt_id)
    if not vt:
        return {"error": "Voice Transaction not found"}, 404
    for key, value in data.items():
        if key == 'processed_at' and value:
            try:
                value = datetime.fromisoformat(value)
            except Exception:
                return {"error": "Invalid processed_at format. Please use ISO format."}, 400
        setattr(vt, key, value)
    db.session.commit()
    return vt.serialize(), 200

def delete_voice_transaction(vt_id):
    vt = VoiceTransaction.query.get(vt_id)
    if not vt:
        return {"error": "Voice Transaction not found"}, 404
    db.session.delete(vt)
    db.session.commit()
    return {"message": "Voice Transaction deleted successfully"}, 200
