from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField 
from wtforms.validators import InputRequired, Length, Optional


class RegisterForm(FlaskForm):
    """User registration form."""

    username = StringField(
        "Username", 
        validators=[InputRequired(), Length(min=5, max=20)]
    )
    
    password = PasswordField(
        "Password", 
        validators=[InputRequired(), Length(min=6, max=50)]
    )

    email = EmailField(
        "Email",
        validators=[InputRequired(), Length(max=50)]
    )
    
    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=30)]
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=30)]
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        "Username", 
        validators=[InputRequired(), Length(min=5, max=20)]
    )
    
    password = PasswordField(
        "Password", 
        validators=[InputRequired(), Length(min=6, max=50)]
    )


class DeleteForm(FlaskForm):
    """Delete User Form - Intentionally BLANK"""


class FeedbackForm(FlaskForm):
    """Add feedback form"""

    title = StringField(
        "Title",
        validators=[InputRequired(), Length(max=100)]
    )

    content = StringField(
        "Content",
        validators=[InputRequired()]
    )