from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username    = StringField("username", validators=[
                    DataRequired(),
                    Length(min=5, max=32)
    ])
    password    = PasswordField("password", validators=[
                    DataRequired(),
                    Length(min=8)
    ])
    remember    = BooleanField("Remember me")
    submit      = SubmitField("login")