from app import db
from app.models.models import Major, Student, Course, ResearchTopic, ProgrammingLanguage, Faculty, ResearchPosition, User
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectField, FloatField, IntegerField 
from wtforms.validators import  Length, DataRequired, Email, EqualTo, ValidationError, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
import sqlalchemy as sqla
from flask import request
from flask_login import current_user


class CourseForm(FlaskForm):
    def get_course_label(a_course):
        instructor = a_course.get_instructor()
        return f"{a_course.title} (Prof. {instructor.firstname} {instructor.lastname})"
        
    title = QuerySelectField("Course",
                             query_factory = lambda :db.session.scalars(sqla.select(Course)), 
                             get_label = get_course_label, 
                             allow_blank = False)
    grade_recieved = SelectField(choices=[("A", "A"), 
                                          ("B", "B"),
                                          ("C", "C"),
                                          ("NR", "NR")])
    
    submit = SubmitField('Post')


class EditForm(FlaskForm):
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
    submit = SubmitField("Save changes")
    def validate_username(self, username):
        query = sqla.select(User).where(User.username == username.data)
        student = db.session.scalars(query).first()
        if student is not None and student.id != current_user.id:
            raise ValidationError('Username already exists. Please provide different username.')
    
    def validate_email(self, email):
        query = sqla.select(User).where(User.email == email.data)
        student = db.session.scalars(query).first()
        if student is not None and student.id != current_user.id:
            raise ValidationError('Email already exists. Please provide different email.')
        
    def validate_wpi_id(self, wpi_id):
        
        id_str = str(wpi_id.data)
        print(id_str)
        if len(id_str) != 9:
            raise ValidationError('Must be a valid WPI ID.')
        
        query = sqla.select(Student).where(Student.wpi_id == wpi_id.data)
        student = db.session.scalars(query).first()
        if student is not None and student.id != current_user.id:
            raise ValidationError('ID is not unique. Please enter your WPI ID.')

class ApplicationFormWithRef(FlaskForm):
    
    
    def get_advisor_name(advisor):
        return f"{advisor.firstname} {advisor.lastname}"
    
    statement = TextAreaField('Statement', validators=[Length(min = 1, max = 1500)])
    faculty_ref = QuerySelectField("Faculty Reference",
                             get_label = get_advisor_name,
                             allow_blank = False)
    submit = SubmitField("Submit Application")

    def __init__(self, position:"ResearchPosition", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.position = position

        self.faculty_ref.query_factory = lambda : db.session.scalars(sqla.select(Faculty).where((Faculty.activated == True) & (Faculty.id != self.position.advisor_id)))

class ApplicationForm(FlaskForm):
    statement = TextAreaField('Statement', validators=[Length(min = 1, max = 1500)])
    submit = SubmitField("Submit Application")

class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")
