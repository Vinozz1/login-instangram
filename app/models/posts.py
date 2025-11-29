from datetime import datetime
from app.extensions import db

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship to user
    user = db.relationship('User', backref=db.backref('posts', lazy=True, order_by='Post.created_at.desc()'))

    def __init__(self, caption, image_url, user_id):
        self.caption = caption
        self.image_url = image_url
        self.user_id = user_id
