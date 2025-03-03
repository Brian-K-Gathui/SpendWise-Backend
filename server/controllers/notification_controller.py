from server.models import db, Notification

def get_all_notifications():
    notifications = [n.serialize() for n in Notification.query.all()]
    return notifications, 200

def get_notification_by_id(notification_id):
    n = Notification.query.get(notification_id)
    if not n:
        return {"error": "Notification not found"}, 404
    return n.serialize(), 200

def create_notification(data):
    required_fields = ['user_id', 'title', 'message']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_n = Notification(
        user_id=data.get('user_id'),
        type=data.get('type'),
        title=data.get('title'),
        message=data.get('message'),
        is_read=data.get('is_read', False)
    )
    db.session.add(new_n)
    db.session.commit()
    return new_n.serialize(), 201

def update_notification(notification_id, data):
    n = Notification.query.get(notification_id)
    if not n:
        return {"error": "Notification not found"}, 404
    for key, value in data.items():
        setattr(n, key, value)
    db.session.commit()
    return n.serialize(), 200

def delete_notification(notification_id):
    n = Notification.query.get(notification_id)
    if not n:
        return {"error": "Notification not found"}, 404
    db.session.delete(n)
    db.session.commit()
    return {"message": "Notification deleted successfully"}, 200
