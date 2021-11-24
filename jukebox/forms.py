from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from jukebox.models import User


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        """Method to validate that a user is not already registered

        Notes:
            This method never needs to be called manually, Flask will call
            it automatically.
        """
        """
        user = User.query.filter_by(username=username_to_check).first()

        if user:
            raise ValidationError("An account with this username already exists.")
        """

    username = StringField(
        label="Username:", validators=[Length(min=2, max=50), DataRequired()]
    )
    password_first = PasswordField(
        label="Password:", validators=[Length(min=6), DataRequired()]
    )
    password_confirm = PasswordField(
        label="Re-type Password:",
        validators=[EqualTo("password_first"), DataRequired()],
    )
    submit = SubmitField(label="Register")


class LoginForm(FlaskForm):
    """Handles all pertinent info related to the login page."""
    username = StringField(label="Username:", validators=[DataRequired()])

    password = PasswordField(label="Password:", validators=[DataRequired()])

    submit = SubmitField(label="Login")


class SessionForm(FlaskForm):
    """Will handle the transmission of a user from home page to session page"""
    session_id = StringField(label="Enter 5 digit session ID")