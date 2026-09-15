from typing import Optional
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from app import db, login
from datetime import datetime, timezone, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask import flash, redirect, url_for
from enum import Enum
from functools import wraps

def student_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_type == "Student":
            return func(*args, **kwargs)
        elif current_user.is_authenticated:
            flash("Student-only page. Faculty restricted.")
            return redirect(url_for('facultymain.mypositions'))
        else:
            flash("Please log in to access this page.")
            return redirect(url_for('studentmain.main'))
    return wrapper

def faculty_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_type == "Faculty":
            return func(*args, **kwargs)
        elif current_user.is_authenticated:
            flash("Faculty-only page. Student restricted.")
            return redirect(url_for('studentmain.index'))
        else:
            flash("Please log in to access this page.")
            return redirect(url_for('studentmain.main'))
    return wrapper

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

students_topics_table = db.Table(
    "students_topics_table",
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('topic_id', sqla.Integer, sqla.ForeignKey('research_topic.topic_id'), primary_key=True))

students_languages_table = db.Table(
    "students_languages_table",
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('lang_id', sqla.Integer, sqla.ForeignKey('programming_language.lang_id'), primary_key=True))

positions_majors_table = db.Table(
   "positions_majors_table",
   db.metadata,
   sqla.Column('major_id', sqla.Integer, sqla.ForeignKey('major.id'), primary_key=True),
   sqla.Column('position_id', sqla.Integer, sqla.ForeignKey('research_position.position_id'), primary_key=True))

positions_courses_table = db.Table(
   "positions_courses_table",
   db.metadata,
   sqla.Column('course_id', sqla.Integer, sqla.ForeignKey('course.id'), primary_key=True),
   sqla.Column('position_id', sqla.Integer, sqla.ForeignKey('research_position.position_id'), primary_key=True))

positions_topics_table = db.Table(
   "positions_topics_table",
   db.metadata,
   sqla.Column('position_id', sqla.Integer, sqla.ForeignKey('research_position.position_id'), primary_key=True),
   sqla.Column('topic_id', sqla.Integer, sqla.ForeignKey('research_topic.topic_id'), primary_key=True))

positions_languages_table = db.Table(
   "positions_languages_table",
   db.metadata,
   sqla.Column('position_id', sqla.Integer, sqla.ForeignKey('research_position.position_id'), primary_key=True),
   sqla.Column('lang_id', sqla.Integer, sqla.ForeignKey('programming_language.lang_id'), primary_key=True))


students_majors_table = db.Table(
    "students_majors_table",
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('major_id', sqla.Integer, sqla.ForeignKey('major.id'), primary_key=True))

class Major(db.Model):
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))
    department : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(150))
    #relationship
    courses : sqlo.WriteOnlyMapped["Course"] = sqlo.relationship(back_populates = 'major', passive_deletes=True)
    students_in_major : sqlo.WriteOnlyMapped["Student"] = sqlo.relationship(
        secondary=students_majors_table,
        primaryjoin=(students_majors_table.c.major_id == id),
        back_populates='majors_of_student',
        passive_deletes=True)

    positions_in_major : sqlo.WriteOnlyMapped["ResearchPosition"] = sqlo.relationship(
       secondary=positions_majors_table,
       primaryjoin = (positions_majors_table.c.major_id == id),
       back_populates = 'preferred_majors',
       passive_deletes=True)

    def __repr__(self):
        return '<Major id: {} - name: {} - department: {}>'.format(self.id,self.name,self.department)

    def get_name(self):
        return self.name

    def get_department(self):
        return self.department

    def get_courses(self):
        query = self.courses.select()
        return db.session.scalars(query).all()

    def get_students(self):
        query = self.students_in_major.select()
        return db.session.scalars(query).all()

    def get_positions(self):
        return db.session.scalars(self.positions.select()).all()

    def to_string(self):
        return self.department + " (" + self.name + ")"


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    firstname : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))
    lastname : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))
    email : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120), index = True, unique = True)
    username : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), index = True, unique = True)
    password_hash : sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(256))
    user_type : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))

    __mapper_args__ = {
        'polymorphic_identity' : 'User',
        'polymorphic_on': user_type
    }

    def __repr__(self):
        return f"<User {self.id} - {self.username} - {self.firstname} - {self.lastname} - ({self.user_type})>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id

    def get_username(self):
         return self.username

    def get_user_type(self):
        return self.user_type

    def get_firstname(self):
        return self.firstname

    def get_lastname(self):
        return self.lastname

    def get_fullname(self):
        return self.firstname + " " + self.lastname

    def get_email(self):
        return self.email

    def get_user_type(self):
        return self.user_type # either "Student" or "Faculty"


class Student(User):
    __tablename__ = "student"
    id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.id), primary_key=True)
    #relationships
    majors_of_student : sqlo.WriteOnlyMapped["Major"] = sqlo.relationship(
         secondary=students_majors_table,
         primaryjoin=(students_majors_table.c.student_id == id),
         back_populates='students_in_major')

    wpi_id : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10), index = True, unique = True)
    gpa : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float, index = True)
    topics_of_interest : sqlo.WriteOnlyMapped["ResearchTopic"] = sqlo.relationship(
        secondary=students_topics_table,
        primaryjoin=students_topics_table.c.student_id == id,
        back_populates='students_interested'
    )
    languages_known : sqlo.WriteOnlyMapped["ProgrammingLanguage"] = sqlo.relationship(
        secondary=students_languages_table,
        primaryjoin=students_languages_table.c.student_id == id,
        back_populates='students'
    )
    courses_taken : sqlo.WriteOnlyMapped["CourseTaken"] = sqlo.relationship(back_populates = 'student_enrolled')
    student_apps : sqlo.WriteOnlyMapped["Application"] = sqlo.relationship(back_populates = 'applicant')

    __mapper_args__ = {
        'polymorphic_identity': 'Student'
        }

    def __repr__(self):
        return '<Student {} - {} - {} {}  - {} - WPI id: {} - GPA: {} - ({})>'.format(
            self.id, self.username, self.firstname, self.lastname, self.email, self.wpi_id, self.gpa, self.user_type)

    def get_wpi_id(self):
        return self.wpi_id

    def get_gpa(self):
        return self.gpa

    def get_majors(self):
        query = self.majors_of_student.select()
        return db.session.scalars(query).all()

    def check_if_taken(self, a_course):
        result = db.session.scalars(self.courses_taken.select().where(CourseTaken.course_id == a_course.id)).first()
        return result is not None

    def add_taken_course(self, a_course, grade):
        if not self.check_if_taken(a_course):
            new_taken_course = CourseTaken(course_name = a_course.get_title(),
                                           course_enrolled = a_course,
                                           student_enrolled = self, grade_recieved = grade)
            db.session.add(new_taken_course)
            db.session.commit()

    def remove_taken_course(self, course_taken):
        db.session.delete(course_taken)
        db.session.commit()

    def taken_courses(self):
        return db.session.scalars(self.courses_taken.select()).all()

    def get_interested_topics(self):
        return db.session.scalars(self.topics_of_interest.select()).all()

    def get_programming_languages(self):
        return db.session.scalars(self.languages_known.select()).all()

    def get_courses_taken(self):
        return db.session.scalars(self.courses_taken.select()).all()

    def get_student_apps(self):
        return db.session.scalars(self.student_apps.select()).all()

    def in_courses(self, course):
        courses = self.taken_courses()
        for c in courses:
            if c.course_id == course.id:
                return True
        return False

    def in_topics(self, topic):
        topics = self.get_interested_topics()
        return topic in topics

    def in_langs(self, lang):
        langs = self.get_programming_languages()
        return lang in langs

    def in_majors(self, major):
        majors = self.get_majors()
        return major in majors

    def is_last_major(self, major):
        majors = self.get_majors()
        last_major = majors[len(majors)-1]
        return major.id == last_major.id

    def has_applied(self, position_id):
        return self.get_application(position_id) is not None

    def get_application(self, position_id):
        return db.session.scalars(self.student_apps.select().where(Application.position_id == position_id)).first()

    def accepted_other_application(self, application_id):
        applications = db.session.scalars(self.student_apps.select().where(Application.application_id != application_id)).all()
        for app in applications:
            if app.application_status == Status.APPROVED:
                return True
        return False

class Faculty(User):
    __tablename__ = "faculty"
    id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.id), primary_key=True)
    department: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(60))
    activated: sqlo.Mapped[bool] = sqlo.mapped_column(sqla.Boolean())
    ref_requests : sqlo.WriteOnlyMapped["Application"] = sqlo.relationship(back_populates = 'faculty_ref')

    #relationships
    positions_posted: sqlo.WriteOnlyMapped["ResearchPosition"] = sqlo.relationship(back_populates="advisor")
    #applications : sqlo.WriteOnlyMapped['Application'] = sqlo.relationship(back_populates='Applications')
    courses_taught : sqlo.WriteOnlyMapped["Course"] = sqlo.relationship(back_populates="instructor")
    __mapper_args__ = {
        'polymorphic_identity': 'Faculty'
        }

    def __repr__(self):
        return "<Faculty Member {} - {} - {} {}  - {} - Department: {})>".format(
            self.id, self.username, self.firstname, self.lastname, self.email,self.department, self.user_type)

    # def get_applications(self):
    #     return self.applications
    def get_courses_taught(self):
        return db.session.scalars(self.courses_taught.select()).all()

    def get_department(self):
        return self.department

    def get_positions_posted(self):
        return db.session.scalars(self.positions_posted.select()).all()

    def set_department(self,depart):
        self.department = depart

    def get_ref_requests(self):
        return db.session.scalars(self.ref_requests.select()).all()

class Course(db.Model):
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    majorid : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Major.id), index=True)
    coursenum : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(4), index = True)
    title : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(150))
    #instructor:
    #relationships
    major : sqlo.Mapped["Major"] = sqlo.relationship(back_populates='courses')
    positions_requiring_course : sqlo.WriteOnlyMapped["ResearchPosition"] = sqlo.relationship(
       secondary=positions_courses_table,
       primaryjoin = (positions_courses_table.c.course_id == id),
       back_populates = 'required_courses',
       passive_deletes=True)
    takes : sqlo.WriteOnlyMapped["CourseTaken"] = sqlo.relationship(
        back_populates='course_enrolled',
        passive_deletes=True)

    instructor_id: sqlo.Mapped[Optional[int]] = sqlo.mapped_column(sqla.ForeignKey(Faculty.id))
    instructor : sqlo.Mapped["Faculty"] = sqlo.relationship(back_populates = 'courses_taught')

    def __repr__(self):
        return '<Course id: {} - coursenum: {} - title: {}>'.format(self.id,self.coursenum,self.title)

    def get_coursenum(self):
        return self.coursenum

    def get_title(self):
        return self.title

    def get_major(self):
        return self.major

    def get_instructor(self):
        return self.instructor

    def get_students(self):
        takes = db.session.scalars(self.takes.select()).all()
        students = []
        for taken in takes:
            students.append(taken.student_enrolled)
        return students

    def to_string(self):
        major = db.session.scalars(sqla.select(Major).where(Major.id == self.majorid)).first()
        return major.name + " " + self.coursenum + ": " + self.title

class CourseTaken(db.Model):
    course_taken_id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    student_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Student.id))
    course_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Course.id))
    course_name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(150))
    grade_recieved: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(1))


    #relationship
    student_enrolled : sqlo.Mapped["Student"] = sqlo.relationship(back_populates='courses_taken')
    course_enrolled : sqlo.Mapped["Course"] = sqlo.relationship(back_populates='takes')

    def get_student(self):
        return self.student_enrolled

    def get_course_id(self):
        return self.course_id

    def get_course_name(self):
        return self.course_name

    def get_course_enrolled(self):
        return self.course_enrolled

    def get_course_instructor_name(self):
        course = self.get_course_enrolled()
        instructor = course.get_instructor()
        name = f"{instructor.firstname} {instructor.lastname}"
        return name

    def __repr__(self):
        return '<Taken course: {} -- Grade Recieved: {}>'.format(self.course_name, self.grade_recieved)

class ResearchTopic(db.Model):
    topic_id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    topic_name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))
    students_interested: sqlo.WriteOnlyMapped["Student"] = sqlo.relationship(
        secondary=students_topics_table,
        primaryjoin=(students_topics_table.c.topic_id == topic_id),
        back_populates='topics_of_interest',
        passive_deletes=True
    )

    positions_with_topic : sqlo.WriteOnlyMapped["ResearchPosition"] = sqlo.relationship(
       secondary=positions_topics_table,
       primaryjoin = (positions_topics_table.c.topic_id == topic_id),
       back_populates = 'research_topics',
       passive_deletes=True
    )


    def __repr__(self):
        return '<Topic id: {} - name: {}>'.format(self.topic_id, self.topic_name)

    def students_with_topic(self):
        return db.session.scalars(self.students_interested.select()).all()

    def to_string(self):
        return self.topic_name

class ProgrammingLanguage(db.Model):
    lang_id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    lang_name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))
    students: sqlo.WriteOnlyMapped["Student"] = sqlo.relationship(
        secondary=students_languages_table,
        primaryjoin=(students_languages_table.c.lang_id == lang_id),
        back_populates='languages_known',
        passive_deletes=True
    )

    positions_requiring_language: sqlo.WriteOnlyMapped["ResearchPosition"] = sqlo.relationship(
       secondary=positions_languages_table,
       primaryjoin = (positions_languages_table.c.lang_id == lang_id),
       back_populates = 'programming_languages',
       passive_deletes=True
    )


    def __repr__(self):
        return '<Language id: {} - name: {}>'.format(self.lang_id, self.lang_name)

    def students_with_lang(self):
        return db.session.scalars(self.students.select()).all()

    def to_string(self):
        return self.lang_name

class ResearchPosition(db.Model):
    position_id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    position_title: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(30))
    description: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120))
    start_date: sqlo.Mapped[Optional[date]] = sqlo.mapped_column(sqla.Date)
    end_date: sqlo.Mapped[Optional[date]] = sqlo.mapped_column(sqla.Date)
    team_size : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)
    min_gpa : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float, index = True)
    advisor_id : sqlo.Mapped[Optional[int]] = sqlo.mapped_column(sqla.ForeignKey(Faculty.id))
    advisor : sqlo.Mapped["Faculty"] = sqlo.relationship(back_populates = 'positions_posted')
    reference_required : sqlo.Mapped[bool] = sqlo.mapped_column(sqla.Boolean())
    position_apps : sqlo.WriteOnlyMapped["Application"] = sqlo.relationship(back_populates = 'position')

    preferred_majors : sqlo.WriteOnlyMapped["Major"] = sqlo.relationship(
        secondary=positions_majors_table,
        primaryjoin = (positions_majors_table.c.position_id == position_id),
        back_populates = 'positions_in_major'
    )

    required_courses : sqlo.WriteOnlyMapped["Course"] = sqlo.relationship(
        secondary=positions_courses_table,
        primaryjoin = (positions_courses_table.c.position_id == position_id),
        back_populates = 'positions_requiring_course'
    )

    research_topics : sqlo.WriteOnlyMapped["ResearchTopic"] = sqlo.relationship(
        secondary=positions_topics_table,
        primaryjoin = (positions_topics_table.c.position_id == position_id),
        back_populates = 'positions_with_topic'
    )

    programming_languages : sqlo.WriteOnlyMapped["ProgrammingLanguage"] = sqlo.relationship(
        secondary=positions_languages_table,
        primaryjoin = (positions_languages_table.c.position_id == position_id),
        back_populates = 'positions_requiring_language'
    )

    def __repr__(self):
        return '<Position ID: {} - Title: {}>'.format(self.position_id, self.position_title)

    def get_position_id(self):
        return self.position_id

    def get_project_title(self):
        return self.position_title

    def get_description(self):
        return self.description

    def get_preferred_majors(self):
        return db.session.scalars(self.preferred_majors.select()).all()

    def get_required_courses(self):
        return db.session.scalars(self.required_courses.select()).all()

    def get_research_topics(self):
        return db.session.scalars(self.research_topics.select()).all()

    def get_required_languages(self):
       return db.session.scalars(self.programming_languages.select()).all()

    def get_advisor_name(self):
        advisor = self.advisor
        return f"{advisor.firstname} {advisor.lastname}"

    def needs_reference(self):
        if self.reference_required:
            return "Yes"
        else:
            return "No"

    def get_position_apps(self):
        return db.session.scalars(self.position_apps.select()).all()

    def get_non_withdrawn_position_apps(self):
        all_apps = self.get_position_apps()
        nw_apps = []
        for app in all_apps:
            if app.application_status != Status.WITHDRAWN:
                nw_apps.append(app)
        return nw_apps


    def get_number_accepted(self, application_id):
        apps = self.get_position_apps()
        accepted_apps: int = 0
        for app in apps:
            if app.application_status == Status.APPROVED and app.application_id != int(application_id):
                accepted_apps += 1
        return accepted_apps

    def in_courses(self, course):
        courses = self.get_required_courses()
        return course in courses

    def in_topics(self, topic):
        topics = self.get_research_topics()
        return topic in topics

    def in_langs(self, lang):
        langs = self.get_required_languages()
        return lang in langs

    def in_majors(self, major):
        majors = self.get_preferred_majors()
        return major in majors

class Status(Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"

class Application(db.Model):
    application_id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    timestamp : sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default = lambda : datetime.now(timezone.utc))
    statement : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(1000))
    position_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(ResearchPosition.position_id))
    position : sqlo.Mapped["ResearchPosition"] = sqlo.relationship(back_populates='position_apps')
    applicant_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Student.id))
    applicant : sqlo.Mapped["Student"] = sqlo.relationship(back_populates='student_apps')
    faculty_ref_id: sqlo.Mapped[Optional[int]] = sqlo.mapped_column(sqla.ForeignKey(Faculty.id))
    faculty_ref : sqlo.Mapped["Faculty"] = sqlo.relationship(back_populates='ref_requests')
    reference_status : sqlo.Mapped[Optional[Status]] = sqlo.mapped_column(sqla.Enum(Status), nullable = True)
    application_status : sqlo.Mapped[Status] = sqlo.mapped_column(sqla.Enum(Status), default = Status.PENDING)

    def __repr__(self):
        return '<Application ID: {} - Submitted by: {} \n  Statement: {} \n App status: {}'.format(self.position_id,
                                                                                                     self.applicant.username,
                                                                                                     self.statement,
                                                                                                     self.application_status.value)

    def get_position(self):
        return self.position

    def get_applicant(self):
        return self.applicant

    def get_faculty_ref(self):
        return self.faculty_ref

    def no_faculty_ref(self):
        return self.faculty_ref is None

    def get_reference_status(self):
        return self.reference_status

    def approve_reference(self):
        self.reference_status = Status.APPROVED

    def reject_reference(self):
        self.reference_status = Status.REJECTED

    def get_application_status(self):
        return self.application_status

    def approve_application(self):
        self.application_status = Status.APPROVED

    def reject_application(self):
        self.application_status = Status.REJECTED

    def withdraw_application(self):
        self.application_status = Status.WITHDRAWN

    def get_position_id(self):
        return self.position_id
