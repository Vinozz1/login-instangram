from datetime import datetime, timedelta
from app.extensions import db

class Story(db.Model):
    __tablename__ = "stories"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('stories', lazy='dynamic', order_by='Story.created_at.desc()'))

    def __init__(self, image_url, user_id):
        self.image_url = image_url
        self.user_id = user_id
        # Stories expire after 24 hours
        self.expires_at = datetime.utcnow() + timedelta(hours=24)

    @property
    def is_expired(self):
        """Check if story has expired"""
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f'<Story {self.id} by User {self.user_id}>'
