from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    # Type: 'like', 'comment', 'follow'
    type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    # Foreign keys
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Who receives the notification
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Who triggered it
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)  # Related post (optional for follows)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # Related comment (for comment notifications)

    # Relationships
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('notifications', lazy='dynamic', order_by='Notification.created_at.desc()'))
    actor = db.relationship('User', foreign_keys=[actor_id])
    post = db.relationship('Post', backref=db.backref('notifications', lazy='dynamic'))
    comment = db.relationship('Comment', backref=db.backref('notifications', lazy='dynamic'))

    def __init__(self, type, recipient_id, actor_id, post_id=None, comment_id=None):
        self.type = type
        self.recipient_id = recipient_id
        self.actor_id = actor_id
        self.post_id = post_id
        self.comment_id = comment_id

    def __repr__(self):
        return f'<Notification {self.type} from User {self.actor_id} to User {self.recipient_id}>'
