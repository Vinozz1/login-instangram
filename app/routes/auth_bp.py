from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from app.forms.loginForm import LoginForm
from app.forms.resetUserForm import ResetUserForm
from app.models.users import User

from app.extensions import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth_bp.route("/reset", methods=["GET", "POST"])
def reset():
    form = ResetUserForm()
    msg = ""

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data)
        if user:
            user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Password reset successful. Please login with your new password.", "success")
        flash("Something wen wrong.", "error")

    return render_template("auth/reset.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    errors = []

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if (user and check_password_hash(user.password, form.password.data)):
            login_user(user)

            next = request.args.get("next")

            return redirect(next or url_for("main.profile"))
        errors.append("Something went wrong.")

    return render_template("auth/login.html", form=form, errors=errors)