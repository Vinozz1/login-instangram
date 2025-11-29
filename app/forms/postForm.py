from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, URL

class PostForm(FlaskForm):
    image_url = StringField("Image URL", validators=[DataRequired(), URL(message="Must be a valid URL")])
    caption = TextAreaField("Caption", validators=[])
    submit = SubmitField("Post")
