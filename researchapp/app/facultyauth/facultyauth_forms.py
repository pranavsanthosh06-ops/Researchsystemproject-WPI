from app import db
from app.models.models import Faculty, User
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, DataRequired, EqualTo, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput, RadioInput
import sqlalchemy as sqla

def get_unactivated_faculty():
    faculty = db.session.scalars(sqla.select(Faculty).where(Faculty.activated == False)).all()
    return faculty

class ActivationForm(FlaskForm):
    email = QuerySelectField(
        'Email',
        query_factory = get_unactivated_faculty,
        get_label = lambda theFaculty : theFaculty.email,
		widget=ListWidget(prefix_label=False),
		option_widget=RadioInput()
    )

    submit = SubmitField("Activate")

class VerifyForm(FlaskForm):
    code = StringField('Verification code', validators=[DataRequired(), Length(min=8, max=8)])

    username = StringField('Username', validators=[DataRequired(), Length(max=32)])
    password = PasswordField('Password', validators=[DataRequired()])
    password_check = PasswordField('Reenter Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField("Verify")
    def validate_username(self, username):
        query = sqla.select(User).where(User.username == username.data)
        faculty = db.session.scalars(query).first()
        if faculty is not None:
            raise ValidationError('Username already exists. Please provide different username.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField('Sign In')
