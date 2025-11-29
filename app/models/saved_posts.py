from datetime import datetime
from app.extensions import db

class SavedPost(db.Model):
    __tablename__ = "saved_posts"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('saved_posts', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('saved_by', lazy='dynamic'))

    # Unique constraint: user can't save same post twice
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_save'),)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

    def __repr__(self):
        return f'<SavedPost User {self.user_id} saved Post {self.post_id}>'
