from flask import Blueprint, render_template
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash,\
                            check_password_hash

from app.extensions import db
from app.forms.signUpForm import SignupForm
from app.models.users import User

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    msg = ""
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            msg = "User already exists"
        else:
            user = User( username=form.username.data,
                        fullname=form.fullname.data,
                        password=generate_password_hash(form.password.data)
                    )
            db.session.add(user)
            db.session.commit()
            msg = "User created."

    return render_template("signup.html", form=form, msg=msg)

@main_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")