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
from app.models.likes import Like
from app.models.comments import Comment
from app.models.follows import Follow

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

@main_bp.route("/like/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)

        # Check if user already liked this post
        existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

        if existing_like:
            # Unlike: delete the like
            db.session.delete(existing_like)
            db.session.commit()
            liked = False
        else:
            # Like: create new like
            new_like = Like(user_id=current_user.id, post_id=post_id)
            db.session.add(new_like)
            db.session.commit()
            liked = True

        # Get updated like count
        like_count = Like.query.filter_by(post_id=post_id).count()

        return {"success": True, "liked": liked, "like_count": like_count}
    except OperationalError:
        return {"success": False, "error": "Database not initialized"}, 500
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@main_bp.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def comment_post(post_id):
    try:
        from flask import request
        data = request.get_json()
        comment_text = data.get('text', '').strip()

        if not comment_text:
            return {"success": False, "error": "Comment cannot be empty"}, 400

        post = Post.query.get_or_404(post_id)
        comment = Comment(text=comment_text, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()

        return {
            "success": True,
            "comment": {
                "id": comment.id,
                "text": comment.text,
                "username": current_user.username,
                "created_at": comment.created_at.strftime('%B %d, %Y')
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@main_bp.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow_user(user_id):
    try:
        if user_id == current_user.id:
            return {"success": False, "error": "Cannot follow yourself"}, 400

        user = User.query.get_or_404(user_id)
        existing_follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()

        if existing_follow:
            # Unfollow
            db.session.delete(existing_follow)
            db.session.commit()
            following = False
        else:
            # Follow
            follow = Follow(follower_id=current_user.id, followed_id=user_id)
            db.session.add(follow)
            db.session.commit()
            following = True

        # Get updated counts
        followers_count = Follow.query.filter_by(followed_id=user_id).count()
        following_count = Follow.query.filter_by(follower_id=user_id).count()

        return {
            "success": True,
            "following": following,
            "followers_count": followers_count,
            "following_count": following_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@main_bp.route("/explore")
@login_required
def explore():
    try:
        # Get posts from users that current_user is NOT following (including own posts)
        followed_ids = [f.followed_id for f in Follow.query.filter_by(follower_id=current_user.id).all()]
        posts = Post.query.filter(Post.user_id.notin_(followed_ids)).order_by(Post.created_at.desc()).all()
        return render_template("explore.html", posts=posts)
    except OperationalError:
        flash("Database not initialized. Please run: flask db upgrade", "error")
        return render_template("explore.html", posts=[])

@main_bp.route("/post/<int:post_id>")
@login_required
def post_detail(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        return render_template("post_detail.html", post=post)
    except Exception as e:
        flash(f"Error loading post: {str(e)}", "error")
        return redirect(url_for("main.feed"))

@main_bp.route("/user/<string:username>")
@login_required
def user_profile(username):
    try:
        user = User.query.filter_by(username=username).first_or_404()
        user_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()

        # Check if current user is following this user
        is_following = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first() is not None

        # Get followers and following counts
        followers_count = Follow.query.filter_by(followed_id=user.id).count()
        following_count = Follow.query.filter_by(follower_id=user.id).count()

        return render_template("user_profile.html",
                             user=user,
                             user_posts=user_posts,
                             is_following=is_following,
                             followers_count=followers_count,
                             following_count=following_count)
    except Exception as e:
        flash(f"Error loading user profile: {str(e)}", "error")
        return redirect(url_for("main.feed"))