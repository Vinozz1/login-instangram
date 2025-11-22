from flask_login import UserMixin

from app.extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True, nullable=False, index=True)
    fullname = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def __init__(self, username, fullname, password):
        self.username = username
        self.fullname = fullname
        self.password = password

    def get_id(self):
        return str(self.id)