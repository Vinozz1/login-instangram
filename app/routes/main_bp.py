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
from app.models.notifications import Notification
from app.models.saved_posts import SavedPost
from app.models.stories import Story
from app.models.messages import Message

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
            # Unlike: delete the like and notification
            db.session.delete(existing_like)
            # Delete the notification if it exists
            notif = Notification.query.filter_by(
                type='like',
                actor_id=current_user.id,
                post_id=post_id
            ).first()
            if notif:
                db.session.delete(notif)
            db.session.commit()
            liked = False
        else:
            # Like: create new like
            new_like = Like(user_id=current_user.id, post_id=post_id)
            db.session.add(new_like)

            # Create notification (only if not liking own post)
            if post.user_id != current_user.id:
                notification = Notification(
                    type='like',
                    recipient_id=post.user_id,
                    actor_id=current_user.id,
                    post_id=post_id
                )
                db.session.add(notification)

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

        # Create notification (only if not commenting on own post)
        if post.user_id != current_user.id:
            notification = Notification(
                type='comment',
                recipient_id=post.user_id,
                actor_id=current_user.id,
                post_id=post_id,
                comment_id=comment.id
            )
            db.session.add(notification)

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
            # Unfollow: delete follow and notification
            db.session.delete(existing_follow)
            # Delete the notification if it exists
            notif = Notification.query.filter_by(
                type='follow',
                actor_id=current_user.id,
                recipient_id=user_id
            ).first()
            if notif:
                db.session.delete(notif)
            db.session.commit()
            following = False
        else:
            # Follow
            follow = Follow(follower_id=current_user.id, followed_id=user_id)
            db.session.add(follow)

            # Create notification
            notification = Notification(
                type='follow',
                recipient_id=user_id,
                actor_id=current_user.id
            )
            db.session.add(notification)

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

# ============= PHASE 2 ROUTES =============

# Notifications
@main_bp.route("/notifications")
@login_required
def notifications():
    """View all notifications"""
    try:
        notifs = Notification.query.filter_by(recipient_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
        # Mark all as read
        for notif in notifs:
            if not notif.is_read:
                notif.is_read = True
        db.session.commit()
        return render_template("notifications.html", notifications=notifs)
    except Exception as e:
        flash(f"Error loading notifications: {str(e)}", "error")
        return redirect(url_for("main.feed"))

@main_bp.route("/notifications/count")
@login_required
def notification_count():
    """Get unread notification count (for badge)"""
    try:
        count = Notification.query.filter_by(recipient_id=current_user.id, is_read=False).count()
        return {"count": count}
    except Exception as e:
        return {"count": 0}

# Search
@main_bp.route("/search")
@login_required
def search():
    """Search for users"""
    from flask import request
    query = request.args.get('q', '').strip()

    if not query:
        return render_template("search.html", users=[], query='')

    # Search by username or fullname
    users = User.query.filter(
        (User.username.ilike(f'%{query}%')) | (User.fullname.ilike(f'%{query}%'))
    ).limit(20).all()

    return render_template("search.html", users=users, query=query)

# Edit Post
@main_bp.route("/post/<int:post_id>/edit", methods=["POST"])
@login_required
def edit_post(post_id):
    """Edit post caption"""
    try:
        from flask import request
        data = request.get_json()
        new_caption = data.get('caption', '').strip()

        post = Post.query.get_or_404(post_id)

        # Check if user owns the post
        if post.user_id != current_user.id:
            return {"success": False, "error": "Unauthorized"}, 403

        post.caption = new_caption
        db.session.commit()

        return {"success": True, "caption": new_caption}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

# Delete Post
@main_bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    """Delete a post"""
    try:
        post = Post.query.get_or_404(post_id)

        # Check if user owns the post
        if post.user_id != current_user.id:
            return {"success": False, "error": "Unauthorized"}, 403

        # Delete all related data (likes, comments, notifications, saved_posts will cascade)
        db.session.delete(post)
        db.session.commit()

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

# Delete Comment
@main_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        comment = Comment.query.get_or_404(comment_id)
        post = Post.query.get(comment.post_id)

        # Check if user owns the comment OR owns the post
        if comment.user_id != current_user.id and post.user_id != current_user.id:
            return {"success": False, "error": "Unauthorized"}, 403

        db.session.delete(comment)
        db.session.commit()

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

# Save/Unsave Post
@main_bp.route("/save/<int:post_id>", methods=["POST"])
@login_required
def save_post(post_id):
    """Save or unsave a post"""
    try:
        post = Post.query.get_or_404(post_id)
        existing_save = SavedPost.query.filter_by(user_id=current_user.id, post_id=post_id).first()

        if existing_save:
            # Unsave
            db.session.delete(existing_save)
            db.session.commit()
            saved = False
        else:
            # Save
            new_save = SavedPost(user_id=current_user.id, post_id=post_id)
            db.session.add(new_save)
            db.session.commit()
            saved = True

        return {"success": True, "saved": saved}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

# Saved Posts Page
@main_bp.route("/saved")
@login_required
def saved_posts():
    """View all saved posts"""
    try:
        saved = SavedPost.query.filter_by(user_id=current_user.id).order_by(SavedPost.created_at.desc()).all()
        posts = [s.post for s in saved]
        return render_template("saved_posts.html", posts=posts)
    except Exception as e:
        flash(f"Error loading saved posts: {str(e)}", "error")
        return redirect(url_for("main.feed"))

# Hashtag Page
@main_bp.route("/hashtag/<string:tag>")
@login_required
def hashtag(tag):
    """View all posts with a specific hashtag"""
    try:
        # Search for posts with hashtag in caption
        posts = Post.query.filter(Post.caption.ilike(f'%#{tag}%')).order_by(Post.created_at.desc()).all()
        return render_template("hashtag.html", tag=tag, posts=posts)
    except Exception as e:
        flash(f"Error loading hashtag: {str(e)}", "error")
        return redirect(url_for("main.feed"))

# Stories
@main_bp.route("/story/create", methods=["POST"])
@login_required
def create_story():
    """Create a new story"""
    try:
        from flask import request
        data = request.get_json()
        image_url = data.get('image_url', '').strip()

        if not image_url:
            return {"success": False, "error": "Image URL required"}, 400

        story = Story(image_url=image_url, user_id=current_user.id)
        db.session.add(story)
        db.session.commit()

        return {"success": True, "story_id": story.id}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@main_bp.route("/stories")
@login_required
def stories():
    """View stories from followed users"""
    try:
        from datetime import datetime
        # Get users that current_user follows
        followed_ids = [f.followed_id for f in Follow.query.filter_by(follower_id=current_user.id).all()]
        followed_ids.append(current_user.id)  # Include own stories

        # Get active stories (not expired)
        active_stories = Story.query.filter(
            Story.user_id.in_(followed_ids),
            Story.expires_at > datetime.utcnow()
        ).order_by(Story.created_at.desc()).all()

        # Group stories by user
        stories_by_user = {}
        for story in active_stories:
            if story.user_id not in stories_by_user:
                stories_by_user[story.user_id] = []
            stories_by_user[story.user_id].append(story)

        return render_template("stories.html", stories_by_user=stories_by_user)
    except Exception as e:
        flash(f"Error loading stories: {str(e)}", "error")
        return redirect(url_for("main.feed"))

# Messages/DMs
@main_bp.route("/messages")
@login_required
def messages():
    """View all message conversations"""
    try:
        # Get all users you've messaged with
        from sqlalchemy import or_
        conversations = db.session.query(User).join(
            Message,
            or_(
                (Message.sender_id == User.id) & (Message.recipient_id == current_user.id),
                (Message.recipient_id == User.id) & (Message.sender_id == current_user.id)
            )
        ).filter(User.id != current_user.id).distinct().all()

        return render_template("messages.html", conversations=conversations)
    except Exception as e:
        flash(f"Error loading messages: {str(e)}", "error")
        return redirect(url_for("main.feed"))

@main_bp.route("/messages/<string:username>")
@login_required
def chat(username):
    """Chat with a specific user"""
    try:
        from sqlalchemy import or_
        other_user = User.query.filter_by(username=username).first_or_404()

        # Get all messages between current_user and other_user
        messages = Message.query.filter(
            or_(
                (Message.sender_id == current_user.id) & (Message.recipient_id == other_user.id),
                (Message.sender_id == other_user.id) & (Message.recipient_id == current_user.id)
            )
        ).order_by(Message.created_at.asc()).all()

        # Mark received messages as read
        for msg in messages:
            if msg.recipient_id == current_user.id and not msg.is_read:
                msg.is_read = True
        db.session.commit()

        return render_template("chat.html", other_user=other_user, messages=messages)
    except Exception as e:
        flash(f"Error loading chat: {str(e)}", "error")
        return redirect(url_for("main.messages"))

@main_bp.route("/messages/<string:username>/send", methods=["POST"])
@login_required
def send_message(username):
    """Send a message to a user"""
    try:
        from flask import request
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return {"success": False, "error": "Message cannot be empty"}, 400

        other_user = User.query.filter_by(username=username).first_or_404()

        message = Message(text=text, sender_id=current_user.id, recipient_id=other_user.id)
        db.session.add(message)
        db.session.commit()

        return {
            "success": True,
            "message": {
                "id": message.id,
                "text": message.text,
                "created_at": message.created_at.strftime('%H:%M'),
                "sender_id": current_user.id
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500