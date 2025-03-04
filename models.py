from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import MetaData, Column, String, DateTime, Boolean

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)


class User(db.Model):
    __tablename__ = 'users'

    id = Column(String(255), primary_key=True)  # This will store the Clerk user ID
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __init__(self, id, email, full_name=None):
        self.id = id
        self.email = email
        self.full_name = full_name

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
