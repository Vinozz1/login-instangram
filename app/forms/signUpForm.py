from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class SignupForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(),
        Length(min=5, max=10)
    ])
    fullname = StringField("Fullname", validators=[
        DataRequired(),
        Length(min=5, max=32)
    ])
    password = PasswordField("Password", validators=[
        DataRequired(),
        EqualTo("confirm", message="Password must macth."),
        Length(min=8)
    ])
    confirm = PasswordField("Confirm", validators=[
        DataRequired(),
        Length(min=8)
    ])
    agreement = BooleanField("I agree", validators=[
        DataRequired()
    ])
    submit = SubmitField("Sign up")