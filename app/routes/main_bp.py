from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash,\
                            check_password_hash
from sqlalchemy.exc import OperationalError

from app.extensions import db
from app.forms.signUpForm import SignupForm
from app.forms.postForm import PostForm
from app.models.users import User
from app.models.posts import Post

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/feed")
@login_required
def feed():
    try:
        # Get all posts ordered by newest first
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template("feed.html", posts=posts)
    except OperationalError:
        flash("Database not initialized. Please run migrations: flask db upgrade", "error")
        return render_template("feed.html", posts=[])

@main_bp.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        try:
            post = Post(
                caption=form.caption.data,
                image_url=form.image_url.data,
                user_id=current_user.id
            )
            db.session.add(post)
            db.session.commit()
            flash("Post created successfully!", "success")
            return redirect(url_for("main.feed"))
        except OperationalError:
            flash("Database not initialized. Please run: flask db upgrade", "error")
            return redirect(url_for("main.profile"))
    return render_template("create_post.html", form=form)

@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            flash("Username already exists. Please choose a different username.", "error")
        else:
            user = User(
                username=form.username.data,
                fullname=form.fullname.data,
                password=generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            flash(f"Account created successfully for {form.username.data}! Please login.", "success")
            return redirect(url_for("auth.login"))

    return render_template("signup.html", form=form)

@main_bp.route("/profile")
@login_required
def profile():
    try:
        # Get current user's posts
        user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
        return render_template("profile.html", user_posts=user_posts)
    except OperationalError:
        flash("Database not initialized. Please run: flask db upgrade", "error")
        return render_template("profile.html", user_posts=[])