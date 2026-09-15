from app import db
from app.models.models import ResearchTopic, ProgrammingLanguage, Major, Course, User, Faculty
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, DateField, IntegerField, FloatField
from wtforms.validators import  Length, DataRequired, Email, EqualTo, ValidationError, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput, RadioInput
import sqlalchemy as sqla
from flask_login import current_user

class DeleteListsForm(FlaskForm):
	majors = QuerySelectMultipleField(
		'Majors',
		query_factory = lambda : db.session.scalars(sqla.select(Major).order_by(Major.department)),
		get_label = lambda theMajor : theMajor.to_string(),
		widget=ListWidget(prefix_label=False),
		option_widget=CheckboxInput()
	)
	courses = QuerySelectMultipleField(
		'Courses',
		query_factory = lambda : db.session.scalars(sqla.select(Course).order_by(Course.title)),
		get_label = lambda theCourse : theCourse.to_string(),
		widget=ListWidget(prefix_label=False),
		option_widget=CheckboxInput()
	)
	topics = QuerySelectMultipleField(
		'Research Topics',
		query_factory = lambda : db.session.scalars(sqla.select(ResearchTopic).order_by(ResearchTopic.topic_name)),
		get_label = lambda theTopic : theTopic.to_string(),
		widget=ListWidget(prefix_label=False),
		option_widget=CheckboxInput()
	)
	languages = QuerySelectMultipleField(
		'Programming Languages',
		query_factory = lambda : db.session.scalars(sqla.select(ProgrammingLanguage).order_by(ProgrammingLanguage.lang_name)),
		get_label = lambda theLang : theLang.to_string(),
		widget=ListWidget(prefix_label=False),
		option_widget=CheckboxInput()
	)

	submit = SubmitField('Delete')

class AddListsForm(FlaskForm):
	new_major_dept = StringField('New Major Title')
	new_major_name = StringField('New Major Abbreviation')
	new_topic = StringField('New Project Topic')
	new_lang = StringField('New Programming Language')

	submit = SubmitField('Add')

	def validate_new_major_name(self, new_major_name):
		if new_major_name.data == "" and self.new_major_dept.data != "":
			raise ValidationError("Fill out both major title and abbreviation to create a new major.")

	def validate_new_major_dept(self, new_major_dept):
		if new_major_dept.data == "" and self.new_major_name.data != "":
			raise ValidationError("Fill out both major title and abbreviation to create a new major.")

class AddCourseForm(FlaskForm):
	new_major = QuerySelectField(
		'Major',
		query_factory = lambda : db.session.scalars(sqla.select(Major).order_by(Major.department)),
		get_label = lambda theMajor : theMajor.to_string(),
		widget=ListWidget(prefix_label=False),
		option_widget=RadioInput(),
		validators=[DataRequired()]
	)
	new_num = IntegerField('Course Number', validators=[DataRequired()])
	new_title = StringField('Course Title', validators=[DataRequired()])
	new_faculty = QuerySelectField(
		'Course Professor',
		query_factory = lambda : db.session.scalars(sqla.select(Faculty).order_by(Faculty.lastname)),
		get_label = lambda theFaculty : "Professor " + theFaculty.firstname + " " + theFaculty.lastname,
		widget=ListWidget(prefix_label=False),
		option_widget=RadioInput(),
		validators=[DataRequired()]
	)

	submit = SubmitField('Add')

	def validate_new_num(self, new_num):
		if len(str(new_num.data)) != 4:
			raise ValidationError('Must be a four-digit number.')

class EditForm(FlaskForm):
	username = StringField('Username', validators = [DataRequired()])
	password = PasswordField('Password', validators = [DataRequired()])
	password_check = PasswordField('Reenter password', validators = [DataRequired(), EqualTo('password')])

	submit = SubmitField('Save changes')

	def validate_username(self, username):
		query = sqla.select(User).where(User.username == username.data)
		faculty = db.session.scalars(query).first()
		if faculty is not None and faculty.id != current_user.id:
			raise ValidationError('Username already exists. Please provide different username.')


class PostPositionForm(FlaskForm):
	position_title =  StringField('Position Title', validators = [DataRequired()])
	description = TextAreaField('Description', validators=[Length(min = 1, max = 200)])
	start_date = DateField('Start Date', format = '%Y-%m-%d', validators=[DataRequired()])
	end_date = DateField('End Date', format = '%Y-%m-%d', validators=[DataRequired()])
	team_size = IntegerField('Team Size', validators=[(DataRequired())])
	min_gpa = FloatField('Minimum Required GPA', validators = [DataRequired(), NumberRange(min=0.0, max=4.0)])
	reference_required = BooleanField("Reference required")
	preferred_majors = QuerySelectMultipleField("Preferred Major(s)",
        query_factory = lambda :db.session.scalars(sqla.select(Major).order_by(Major.name)),
        get_label = lambda aMajor : aMajor.name,
        widget = ListWidget(prefix_label=False),
        option_widget = CheckboxInput())
	research_topics = QuerySelectMultipleField('Required Research Topics',
                                    query_factory= lambda: db.session.scalars(sqla.select(ResearchTopic)).all(),
                                    get_label= lambda thetopic : thetopic.topic_name,
                                    widget=ListWidget(prefix_label=False),
                                    option_widget=CheckboxInput())
	required_languages = QuerySelectMultipleField('Required Programming Languages',
                                    query_factory= lambda: db.session.scalars(sqla.select(ProgrammingLanguage)).all(),
                                    get_label= lambda thelang : thelang.lang_name,
                                    widget=ListWidget(prefix_label=False),
                                    option_widget=CheckboxInput())
	required_courses = QuerySelectMultipleField('Required Coursework',
                                    query_factory= lambda: db.session.scalars(sqla.select(Course)).all(),
                                    get_label= lambda thecourse : thecourse.title,
                                    widget=ListWidget(prefix_label=False),
                                    option_widget=CheckboxInput())
	submit = SubmitField("Post")

	def validate_end_date(self, end_date):
		if self.start_date.data >= end_date.data:
			raise ValidationError('End date must occur after start date.')


class SortForm(FlaskForm):
    posted_by_me = BooleanField("View my positions only")
    submit = SubmitField('Refresh')

class ApproveForm(FlaskForm):
	submit = SubmitField('Approve')

class DenyForm(FlaskForm):
	submit = SubmitField('Deny')

# class CourseForm(FlaskForm):
#     coursenum = StringField('Course Number',[Length(min=3, max=6)])
#     title = StringField('Cours Title', validators = [DataRequired()])
#     major = QuerySelectField("Major",
#                              query_factory = lambda :db.session.scalars(sqla.select(Major)),
#                              get_label = lambda aMajor : aMajor.name,
#                              allow_blank = False)
#     submit = SubmitField('Post')


# class EditForm(FlaskForm):
#     firstname = StringField('First Name', validators = [DataRequired()])
#     lastname = StringField('Last Name', validators = [DataRequired()])
#     email = StringField('Email', validators = [DataRequired(), Email()])
#     address = TextAreaField('Address', validators = [Length(min = 0, max = 200)])
#     password = PasswordField('Password', validators = [DataRequired()])
#     repassword = PasswordField('Password', validators = [DataRequired(), EqualTo('password')])
#     submit = SubmitField('Post')
#     majors = QuerySelectMultipleField("Major",
#         query_factory = lambda :db.session.scalars(sqla.select(Major).order_by(Major.name)),
#         get_label = lambda aMajor : aMajor.name,
#         widget = ListWidget(prefix_label=False),
#         option_widget = CheckboxInput())


#     def validate_email(self, email):
#         query = sqla.select(Student).where(Student.email == email.data)
#         student = db.session.scalars(query).first()
#         if student is not None:
#             if student.id != current_user.id:
#                 raise ValidationError('Email already exists. Please provide different email')

class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


