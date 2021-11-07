from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class RegisterForm(FlaskForm):
    username = StringField(
        label="Username:", validators=[Length(min=2, max=50), DataRequired()]
    )
    password_init = PasswordField(
        label="Password:", validators=[Length(min=6), DataRequired()]
    )
    password_confirm = PasswordField(
        label="Re-type Password:", validators=[EqualTo("password_init"), DataRequired()]
    )
    submit = SubmitField(label="Submit")
