import os
import pytest
from app import create_app, db
from app.models.models import Student, Faculty, User, Major, ProgrammingLanguage, ResearchTopic, ResearchPosition, Course,CourseTaken, Application, Status
from config import Config
from datetime import date
import sqlalchemy as sqla

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'bad-bad-key'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    TESTING = True


@pytest.fixture(scope='module')
def test_client():
    # create the flask application ; configure the app for tests
    flask_app = create_app(config_class=TestConfig)

    # db.init_app(flask_app)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield  testing_client
    # this is where the testing happens!

    ctx.pop()

def new_student_user(username, email, firstname, lastname, wpi_id, gpa, password):
    user = Student(username = username, email = email, firstname = firstname, lastname = lastname, wpi_id = wpi_id, gpa=gpa )
    user.set_password(password)
    return user

def new_faculty_user(username, email, firstname, lastname, department, activated, password):
    user = Faculty(username = username, email = email, firstname = firstname, lastname = lastname, department = department, activated=activated )
    user.set_password(password)
    return user

@pytest.fixture
def init_database(request,test_client):
    # Create the database and the database table
    db.create_all()
    # initialize the majors
    if Major.query.count() == 0:
        majors = [{'name':'CS','department':'Computer Science'},{'name':'SE','department':'Computer Science'},{'name':'EE','department':'Electrical Engineering'},
                  {'name':'ME','department':'Mechanical Engineering'}, {'name':'MATH','department': 'Mathematics'}  ]
        for m in majors:
            db.session.add(Major(name=m['name'],department=m['department']))
        db.session.commit()

    if ProgrammingLanguage.query.count() == 0:
        languages = ["Java", "Python", "C/C++"]
        for l in languages:
            db.session.add(ProgrammingLanguage(lang_name = l))
        db.session.commit()

    if ResearchTopic.query.count() == 0:
        topics = ["Machine Learning", "Operating Systems", "Robotics Applications"]
        for t in topics:
            db.session.add(ResearchTopic(topic_name = t))
        db.session.commit()

    #add a student
    stud1 = new_student_user(firstname="Bob", lastname = "Dylan", email="bob@gmail.com",username="bob",
                wpi_id = "901013026", gpa = 3.8, password="123")
    db.session.add(stud1)
    db.session.commit()
    #add a faculty member
    fac1 = new_faculty_user(firstname="Scooby", lastname = "Doo", email="scooby@gmail.com",username="scooby", department = "RBE", activated=True, password="123")
    db.session.add(fac1)
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()

def do_login(test_client, path , username, passwd):
    response = test_client.post(path,
                          data=dict(username= username, password=passwd, remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Hello," in response.data

def do_logout(test_client):
    response = test_client.get("/student/logout",
                          follow_redirects = True)
    assert response.status_code == 200
    # Assuming the application re-directs to login page after logout.
    assert b"Sign In" in response.data   #Students should update this assertion condition according to their own page content

#Ritvik's tests
def test_student_register_page(request, test_client, init_database):
    response = test_client.get('/student/register', follow_redirects = True)
    assert response.status_code == 200
    assert b"Register" in response.data

def test_student_login_page(request, test_client, init_database):
    response = test_client.get('/student/login', follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def tes_student_register(request, test_client, init_database):
    response = test_client.post(
        '/student/register',
        data=dict(firstname="Morgan", lastname="Shia", username="morgan", email="mshia@wpi.edu", wpi_id=123456789, password="123", repassword="123", gpa=3.0),
        follow_redirects = True
    )

    assert response.status_code == 200
    assert b"You are now a registered user." in response.data
    new_user = db.session.scalars(sqla.select(User).where(User.firstname == "Morgan")).first()
    assert new_user.user_type == "Student"
    assert new_user.username == "morgan"
    assert new_user.email == "mshia@wpi.edu"

def test_student_login_failed(request, test_client, init_database):
    response = test_client.post(
        '/student/login',
        data=dict(username="vanya", password="123", remember_me=True),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Unsuccessful login attempt" in response.data

#Pranav's Tests
#INSERT TESTS HERE
def test_view_position_details(test_client, init_database):
    fac = Faculty.query.first()
    pos = ResearchPosition(
        position_title="ML Research",
        description="Test pos",
        start_date=None,
        end_date=None,
        team_size=2,
        min_gpa=3.0,
        advisor=fac,
        reference_required=False
    )
    db.session.add(pos)
    db.session.commit()

    do_login(test_client,'/student/login', "bob", "123")
    r = test_client.get(f"/positions/{pos.position_id}")
    assert r.status_code == 200
    assert b"ML Research" in r.data
    do_logout(test_client)


def test_apply_position_post_no_reference(test_client, init_database):
    student = Student.query.filter_by(username="bob").first()
    fac = Faculty.query.first()
    pos = ResearchPosition(
        position_title="OS Research",
        description="Kernel",
        start_date=None,
        end_date=None,
        team_size=1,
        min_gpa=3.0,
        advisor=fac,
        reference_required=False
    )
    db.session.add(pos)
    db.session.commit()

    do_login(test_client, '/student/login', "bob", "123")
    test_client.post(f"/positions/{pos.position_id}/apply", data=dict(statement="Hi"), follow_redirects=True)

    app = Application.query.filter_by(applicant_id=student.id, position_id=pos.position_id).first()
    assert app is not None
    do_logout(test_client)


def test_add_course_create_taken_course(test_client, init_database):
    major = Major.query.first()
    fac = Faculty.query.first()
    course = Course(major=major, coursenum="2223", title="Algorithms", instructor=fac)
    db.session.add(course)
    db.session.commit()

    student = Student.query.filter_by(username="bob").first()

    do_login(test_client, '/student/login', "bob", "123")
    test_client.post("/course/create", data=dict(title=course.id, grade_recieved="A"), follow_redirects=True)

#Ritvik's tests
#INSERT TESTS HERE
    taken = CourseTaken.query.filter_by(student_id=student.id, course_id=course.id).first()
    assert taken is not None
    do_logout(test_client)

#Vanya's tests
#INSERT TESTS HERE

#Pranav's Tests
#INSERT TESTS HERE
def test_delete_course_taken(test_client, init_database):
    major = Major.query.first()
    fac = Faculty.query.first()
    course = Course(major=major, coursenum="1111", title="Test Course", instructor=fac)
    db.session.add(course)
    db.session.commit()

    student = Student.query.filter_by(username="bob").first()
    ct = CourseTaken(
        student_enrolled=student,
        course_enrolled=course,
        student_id=student.id,
        course_id=course.id,
        course_name=course.title,
        grade_recieved="B"
    )
    db.session.add(ct)
    db.session.commit()

    do_login(test_client, "/student/login", "bob", "123")
    cid = ct.course_taken_id
    test_client.post(f"/course/{cid}/delete", data={}, follow_redirects=True)
    assert CourseTaken.query.get(cid) is None
    do_logout(test_client)


def test_view_all_applications(test_client, init_database):
    student = Student.query.filter_by(username="bob").first()
    fac = Faculty.query.first()

    pos = ResearchPosition(
        position_title="Robotics",
        description="Robotics apps",
        start_date=None,
        end_date=None,
        team_size=3,
        min_gpa=3.0,
        advisor=fac,
        reference_required=False
    )
    db.session.add(pos)
    db.session.commit()

    app = Application(statement="I like robots", position=pos, applicant=student, application_status=Status.PENDING)
    db.session.add(app)
    db.session.commit()

    do_login(test_client, "/student/login", "bob", "123")
    r = test_client.get("/applications")
    assert r.status_code == 200
    assert b"Robotics" in r.data
    do_logout(test_client)


def test_view_specific_application(test_client, init_database):
    student = Student.query.filter_by(username="bob").first()
    fac = Faculty.query.first()

    pos = ResearchPosition(
        position_title="Data Science",
        description="Data",
        start_date=None,
        end_date=None,
        team_size=2,
        min_gpa=3.0,
        advisor=fac,
        reference_required=False
    )
    db.session.add(pos)
    db.session.commit()

    app = Application(statement="I like data", position=pos, applicant=student, application_status=Status.PENDING)
    db.session.add(app)
    db.session.commit()

    do_login(test_client, "/student/login", "bob", "123")
    r = test_client.get(f"/applications/{app.application_id}/view")
    assert r.status_code == 200
    assert b"I like data" in r.data
    do_logout(test_client)


def test_withdraw_application(test_client, init_database):
    student = Student.query.filter_by(username="bob").first()
    fac = Faculty.query.first()

    pos = ResearchPosition(
        position_title="Withdraw Position",
        description="Test",
        start_date=None,
        end_date=None,
        team_size=1,
        min_gpa=3.0,
        advisor=fac,
        reference_required=False
    )
    db.session.add(pos)
    db.session.commit()

    app = Application(statement="Withdraw", position=pos, applicant=student, application_status=Status.PENDING)
    db.session.add(app)
    db.session.commit()

    do_login(test_client, "/student/login", "bob", "123")
    r = test_client.post(f"/applications/{app.application_id}/withdraw", data={}, follow_redirects=True)
    assert r.status_code in (200, 302)
    do_logout(test_client)

#Elliot's Tests
#INSERT TESTS HERE


def test_student_profile_route(test_client, init_database):
    do_login(test_client,"/student/login", "bob", "123")
    r = test_client.get("/student/profile")
    assert r.status_code == 200
    assert b"Bob" in r.data
    do_logout(test_client)

#Elliot's Tests

def test_main(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the welcome page is displayed for unauthenticated users
    """
    response = test_client.get('/',follow_redirects=True)
    assert response.status_code == 200

def test_index(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/index' page is requested (GET)
    THEN check that authenticated students can access the index page
    """
    do_login(test_client, path='/student/login', username='bob', passwd='123')
    response = test_client.get('/index', follow_redirects=True)
    assert response.status_code == 200
    do_logout(test_client)

def test_position_details(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/positions/<position_id>' page is requested (GET)
    THEN check that position details are displayed correctly
    """
    fac = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).first()
    from app.models.models import ResearchPosition
    pos = ResearchPosition(
                            position_title="ML Research Position",
                            description="Work on machine learning",
                            start_date=date(2025, 5, 1),
                            end_date=date(2025, 12, 31),
                            team_size=3,
                            min_gpa=3.5,
                            advisor_id=fac.get_id(),
                            reference_required=False)
    db.session.add(pos)
    db.session.commit()

    response = test_client.get(f'/positions/{pos.position_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"ML Research Position" in response.data
    assert b"Work on machine learning" in response.data

def test_addclass(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/course/create' page is requested (GET)
    THEN check that students can access the add course page
    """
    do_login(test_client, path='/student/login', username='bob', passwd='123')
    response = test_client.get('/course/create', follow_redirects=True)
    assert response.status_code == 200
    do_logout(test_client)

def test_edit_profile(test_client, init_database):
    do_login(test_client,'/student/login', "bob", "123")
    response = test_client.get("/student/editprofile", follow_redirects = True)
    assert response.status_code == 200
    assert b"Bob" in response.data

    bob = db.session.scalars(sqla.select(Student).where(Student.username == "bob")).first()
    bob.topics_of_interest.add(db.session.scalars(sqla.select(ResearchTopic).where(ResearchTopic.topic_name == "Machine Learning")).first())
    bob.languages_known.add(db.session.scalars(sqla.select(ProgrammingLanguage).where(ProgrammingLanguage.lang_name == "Python")).first())
    bob.majors_of_student.add(db.session.scalars(sqla.select(Major).where(Major.name == "CS")).first())
    db.session.add(bob)
    db.session.commit()

    response = test_client.post(f"/student/editprofile", data=dict(firstname="Bobby", lastname = "Dylan", username = "bob",
                                                                   email = "bob@gmail.com", wpi_id = 901013026, gpa = 4.1,
                                                                   password="123", repassword = "123", submit = "Save changes"), follow_redirects = True)
    assert response.status_code == 200
    assert b"Must be a number between 0.0 and 4.0"

    major2 = db.session.scalars(sqla.select(Major).where(Major.name == "MATH")).first()
    lang2 = db.session.scalars(sqla.select(ProgrammingLanguage).where(ProgrammingLanguage.lang_name == "Java")).first()
    topic2 = db.session.scalars(sqla.select(ResearchTopic).where(ResearchTopic.topic_name == "Machine Learning")).first()


    response = test_client.post(f"/student/editprofile", data=dict(firstname="Bobby", lastname = "Dylan", username = "bob",
                                                                   email = "bob@gmail.com", wpi_id = 901013026, gpa = 3.2,
                                                                   password="123", repassword = "123",
                                                                   majors = [str(major2.id)],
                                                                   research_topics = [str(topic2.topic_id)],
                                                                   programming_languages = [str(lang2.lang_id)],
                                                                   submit = "Save changes"), follow_redirects = True)
    print(response.data)
    assert response.status_code == 200
    assert b"Your changes have been made" in response.data
    #check updates to database
    bob2 = db.session.scalars(sqla.select(Student).where(Student.firstname == "Bobby")).first()
    assert bob2 is not None
    assert major2 in bob2.get_majors()
    assert lang2 in bob2.get_programming_languages()
    assert topic2 in bob2.get_interested_topics()

    response = test_client.post(f"/student/editprofile", data=dict(firstname="Bobby", lastname = "Dylan", username = "bob",
                                                                   email = "bob@gmail.com", wpi_id = 901013026, gpa = 3.2,
                                                                   password="123", repassword = "123",
                                                                   submit = "Save changes"), follow_redirects = True)
    assert response.status_code == 200
    assert len(bob2.get_majors()) == 0
    assert len(bob2.get_programming_languages()) == 0
    assert len(bob2.get_interested_topics()) == 0
    do_logout(test_client)

def test_view_position_details_data(test_client, init_database):
    fac = Faculty.query.first()
    pos = ResearchPosition(
        position_title="ML Research",
        description="Test pos",
        start_date=None,
        end_date=None,
        team_size=2,
        min_gpa=3.0,
        advisor=fac,
        reference_required=False
    )
    db.session.add(pos)
    db.session.commit()

    do_login(test_client,'/student/login', "bob", "123")
    r = test_client.get(f"/positions/{pos.position_id}/data")
    assert r.status_code == 200
    assert b"ML Research" in r.data
    do_logout(test_client)

