from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, Length, DataRequired


class ResetUserForm(FlaskForm):
    username            = StringField("username", validators=[DataRequired()])
    new_password        = PasswordField("new password", validators=[Length(min=8)])
    confirm_password    = PasswordField("confirm password", validators=[
                            Length(min=8), 
                            EqualTo(new_password)])
    submit              = SubmitField("submit")