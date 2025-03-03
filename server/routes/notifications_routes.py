from flask import request
from flask_restful import Resource
from server.controllers.notification_controller import (
    get_all_notifications,
    get_notification_by_id,
    create_notification,
    update_notification,
    delete_notification
)

class NotificationsResource(Resource):
    def get(self):
        notifications, status_code = get_all_notifications()
        return notifications, status_code

    def post(self):
        data = request.get_json()
        n, status_code = create_notification(data)
        return n, status_code

class NotificationByIdResource(Resource):
    def get(self, notification_id):
        n, status_code = get_notification_by_id(notification_id)
        return n, status_code

    def patch(self, notification_id):
        data = request.get_json()
        n, status_code = update_notification(notification_id, data)
        return n, status_code

    def delete(self, notification_id):
        response, status_code = delete_notification(notification_id)
        return response, status_code
