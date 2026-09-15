from app import db
from app.models.models import Student, Major, ProgrammingLanguage, ResearchTopic, User
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, IntegerField, FloatField
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import  Length, DataRequired, Email, EqualTo, ValidationError, NumberRange
import sqlalchemy as sqla

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    firstname = StringField('First Name', validators = [DataRequired()])
    lastname = StringField('Last Name', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    repassword = PasswordField('Confirm password', validators = [DataRequired(), EqualTo('password')])
    wpi_id = IntegerField("WPI ID", validators=[DataRequired()])
    gpa = FloatField('Cumulative GPA', validators = [DataRequired(), NumberRange(min=0.0, max=4.0)])

    majors = QuerySelectMultipleField("Major",
        query_factory = lambda :db.session.scalars(sqla.select(Major).order_by(Major.name)), 
        get_label = lambda aMajor : aMajor.name,
        widget = ListWidget(prefix_label=False),
        option_widget = CheckboxInput())
    
    research_topics = QuerySelectMultipleField('Research Topics of Interest', 
                                    query_factory= lambda: db.session.scalars(sqla.select(ResearchTopic)).all(),
                                    get_label= lambda thetopic : thetopic.topic_name,
                                    widget=ListWidget(prefix_label=False), 
                                    option_widget=CheckboxInput())
    programming_languages = QuerySelectMultipleField('Programming Languages', 
                                    query_factory= lambda: db.session.scalars(sqla.select(ProgrammingLanguage)).all(),
                                    get_label= lambda thelang : thelang.lang_name,
                                    widget=ListWidget(prefix_label=False), 
                                    option_widget=CheckboxInput())
    
    submit = SubmitField('Create Account')
    
    def validate_username(self, username):
        query = sqla.select(User).where(User.username == username.data)
        student = db.session.scalars(query).first()
        if student is not None:
            raise ValidationError('Username already exists. Please provide different username.')
    
    def validate_email(self, email):
        query = sqla.select(User).where(User.email == email.data)
        student = db.session.scalars(query).first()
        if student is not None:
            raise ValidationError('Email already exists. Please provide different email.')
        
    def validate_wpi_id(self, wpi_id):
        
        id_str = str(wpi_id.data)
        print(id_str)
        if len(id_str) != 9:
            raise ValidationError('Must be a valid WPI ID.')
        
        query = sqla.select(Student).where(Student.wpi_id == wpi_id.data)
        student = db.session.scalars(query).first()
        if student is not None:
            raise ValidationError('ID is not unique. Please enter your WPI ID.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField('Sign In')

