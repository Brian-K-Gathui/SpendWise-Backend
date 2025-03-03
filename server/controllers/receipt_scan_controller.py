from datetime import datetime
from server.models import db, ReceiptScan

def get_all_receipt_scans():
    scans = [scan.serialize() for scan in ReceiptScan.query.all()]
    return scans, 200

def get_receipt_scan_by_id(scan_id):
    scan = ReceiptScan.query.get(scan_id)
    if not scan:
        return {"error": "Receipt Scan not found"}, 404
    return scan.serialize(), 200

def create_receipt_scan(data):
    required_fields = ['user_id']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    new_scan = ReceiptScan(
        user_id=data.get('user_id'),
        image_url=data.get('image_url'),
        ocr_text=data.get('ocr_text'),
        confidence_score=data.get('confidence_score'),
        merchant_name=data.get('merchant_name'),
        purchase_date=data.get('purchase_date'),
        items_detected=data.get('items_detected'),
        total_amount=data.get('total_amount'),
        status=data.get('status', 'processing')
    )

    # If purchase_date is provided, convert it to a datetime object
    if new_scan.purchase_date:
        try:
            new_scan.purchase_date = datetime.fromisoformat(new_scan.purchase_date)
        except Exception:
            return {"error": "Invalid purchase_date format. Please use ISO format."}, 400

    # If processed_at is provided, convert it to a datetime object
    if data.get('processed_at'):
        try:
            new_scan.processed_at = datetime.fromisoformat(data.get('processed_at'))
        except Exception:
            return {"error": "Invalid processed_at format. Please use ISO format."}, 400

    db.session.add(new_scan)
    db.session.commit()
    return new_scan.serialize(), 201

def update_receipt_scan(scan_id, data):
    scan = ReceiptScan.query.get(scan_id)
    if not scan:
        return {"error": "Receipt Scan not found"}, 404

    allowed_fields = {
        'image_url', 'ocr_text', 'confidence_score', 'merchant_name', 
        'purchase_date', 'items_detected', 'total_amount', 'status', 'processed_at'
    }
    for key, value in data.items():
        if key in allowed_fields:
            if key in ['purchase_date', 'processed_at'] and value:
                try:
                    value = datetime.fromisoformat(value)
                except Exception:
                    return {"error": f"Invalid {key} format. Please use ISO format."}, 400
            setattr(scan, key, value)
    db.session.commit()
    return scan.serialize(), 200

def delete_receipt_scan(scan_id):
    scan = ReceiptScan.query.get(scan_id)
    if not scan:
        return {"error": "Receipt Scan not found"}, 404
    db.session.delete(scan)
    db.session.commit()
    return {"message": "Receipt Scan deleted successfully"}, 200
