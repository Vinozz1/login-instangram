from flask import Flask

import os
from dotenv import load_dotenv

from app.extensions import db, migrate, login_manager
from app.configs import DevConf, ProdConf

from app.routes.main_bp import main_bp
from app.routes.auth_bp import auth_bp

# Import models for migrations
from app.models.users import User
from app.models.posts import Post
from app.models.likes import Like
from app.models.comments import Comment
from app.models.follows import Follow

load_dotenv()

isDev = os.getenv("FLASK_DEBUG")

def create_app():
    # App Factory
    app = Flask(__name__)

    if isDev:
        app.config.from_object(DevConf)
    else:
        app.config.from_object(ProdConf)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Register Bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    return app