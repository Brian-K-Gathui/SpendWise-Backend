from flask_restful import Resource, reqparse
from flask import g, request
from models import db, Notification, User
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

logger = logging.getLogger(__name__)

class NotificationResource(Resource):
    def get(self, notification_id=None):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Check if we need to mark all as read
            mark_all_read = request.args.get('mark_all_read', 'false').lower() == 'true'
            if mark_all_read:
                notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
                for notification in notifications:
                    notification.is_read = True
                db.session.commit()
                return {
                    "message": "All notifications marked as read",
                    "count": len(notifications)
                }

            # If notification_id is provided, get that specific notification
            if notification_id:
                notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
                if not notification:
                    return {"error": "Notification not found or access denied"}, 404

                return notification.to_dict()

            # Otherwise, return all notifications for the user
            notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
            return [notification.to_dict() for notification in notifications]

        except OperationalError as e:
            logger.error(f"Database connection error in GET /notifications: {str(e)}")
            db.session.rollback()
            return {"error": "Database connection error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error in GET /notifications: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('title', type=str, required=True, help='Title is required')
            parser.add_argument('message', type=str, required=True, help='Message is required')
            parser.add_argument('type', type=str, required=True, help='Type is required')
            args = parser.parse_args()

            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            # Create new notification
            new_notification = Notification(
                user_id=user_id,
                title=args['title'],
                message=args['message'],
                type=args['type']
            )

            try:
                db.session.add(new_notification)
                db.session.commit()
                return {
                    "message": "Notification created successfully",
                    "notification": new_notification.to_dict()
                }, 201
            except Exception as e:
                logger.error(f"Error creating notification: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in POST /notifications: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, notification_id):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the notification
            notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
            if not notification:
                return {"error": "Notification not found or access denied"}, 404

            # Parse the request data
            parser = reqparse.RequestParser()
            parser.add_argument('is_read', type=bool, required=False)
            args = parser.parse_args()

            # Update is_read if provided
            if args.get('is_read') is not None:
                notification.is_read = args['is_read']

            try:
                db.session.commit()
                return {
                    "message": "Notification updated successfully",
                    "notification": notification.to_dict()
                }
            except Exception as e:
                logger.error(f"Error updating notification: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in PUT /notifications/{notification_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, notification_id):
        try:
            # Get the Clerk user ID from the JWT token
            user_id = g.user.get('sub')
            if not user_id:
                return {"error": "User ID not found in token"}, 400

            # Find the notification
            notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
            if not notification:
                return {"error": "Notification not found or access denied"}, 404

            try:
                db.session.delete(notification)
                db.session.commit()
                return {
                    "message": "Notification deleted successfully"
                }
            except Exception as e:
                logger.error(f"Error deleting notification: {str(e)}")
                db.session.rollback()
                return {"error": str(e)}, 500

        except Exception as e:
            logger.error(f"Error in DELETE /notifications/{notification_id}: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500
