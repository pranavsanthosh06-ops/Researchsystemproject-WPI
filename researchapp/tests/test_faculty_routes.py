import os
import pytest
from app import create_app, db
from flask import session
from app.models.models import Student, Faculty, Major, ProgrammingLanguage, ResearchTopic, ResearchPosition, Application, Status, Course, Major
from config import Config
import sqlalchemy as sqla
from datetime import date

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

def new_student_user(username, email, firstname, lastname, wpi_id, gpa, passwd):
    user = Student(username = username, email = email, firstname = firstname, lastname = lastname, wpi_id = wpi_id, gpa=gpa )
    user.set_password(passwd)
    return user

def new_faculty_user(username, email, firstname, lastname, department, activated, passwd):
    user = Faculty(username = username, email = email, firstname = firstname, lastname = lastname, department = department, activated=activated )
    user.set_password(passwd)
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
                wpi_id = "901013026", gpa = 3.8, passwd = "123")
    db.session.add(stud1)
    db.session.commit()
    #add a faculty member
    fac1 = new_faculty_user(firstname="Scooby", lastname = "Doo", email="scooby@gmail.com",username="scooby", department = "RBE",
                            activated=True, passwd = "123")
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

def do_logout(test_client, path):
    response = test_client.get(path,
                          follow_redirects = True)
    assert response.status_code == 200
    # Assuming the application re-directs to login page after logout.
    assert b"Sign In" in response.data   #Students should update this assertion condition according to their own page content

#Ritvik's tests
def test_faculty_activate_page(request, test_client, init_database):
    response = test_client.get('/faculty/activate', follow_redirects = True)
    assert response.status_code == 200
    assert b"Activate your account" in response.data

def test_faculty_login_page(request, test_client, init_database):
    response = test_client.get('/faculty/login', follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_faculty_login_failed(request, test_client, init_database):
    response = test_client.post(
        '/faculty/login',
        data=dict(username="vanya", password="123", remember_me=True),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Invalid username or password!" in response.data

#Vanya's tests
def test_student_accessing_faculty_page(request,test_client, init_database):
    do_login(test_client, path = '/student/login', username = 'bob', passwd = '123')
    #test edit-lists
    response = test_client.get('/faculty/edit-lists', follow_redirects = True)
    assert response.status_code == 200
    assert b"Faculty-only page. Student restricted." in response.data

    #test faculty profile
    response = test_client.get("/faculty/profile", follow_redirects = True)
    assert response.status_code == 200
    assert b"Faculty-only page. Student restricted." in response.data

    #test /position/mypositions
    response = test_client.get("/position/mypositions", follow_redirects = True)
    assert response.status_code == 200
    assert b"Faculty-only page. Student restricted." in response.data

    response = test_client.get(f"/faculty/{1}/profile", follow_redirects = True)
    assert response.status_code == 200
    assert b"Faculty-only page. Student restricted." in response.data

    response = test_client.get(f"faculty/requests", follow_redirects = True)
    assert response.status_code == 200
    assert b"Faculty-only page. Student restricted." in response.data


    #log out
    do_logout(test_client, path = '/student/logout')

def test_edit_lists(request,test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/edit-lists' page is requested (POST)
    THEN check that the response is valid
    """
    do_login(test_client, path = '/faculty/login', username = 'scooby', passwd = '123')
    # Create a test client using the Flask application configured for testing

    response = test_client.get('/faculty/edit-lists')

    # TO DO : write assert statements:
    #   verifying the status code and
    #   verifying the response content.
    assert response.status_code == 200
    assert b"Remove Elements" in response.data
    topics = db.session.scalars(sqla.select(ResearchTopic)).all()
    for t in topics:
        assert b"Java" in response.data
    assert b"Add Elements" in response.data
    assert b"Add Course" in response.data

    #Try adding elements
    response = test_client.post('/faculty/edit-lists/add',
                               data=dict(new_topic = 'Robotics in Medicine', new_lang = "Ruby on Rails", new_major_name = "BME", new_major_dept = "Biomedical Engineering", submit = "Add"),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Robotics in Medicine" in response.data
    assert b"Ruby on Rails" in response.data
    assert b"Biomedical Engineering (BME)" in response.data
    assert b"Python" in response.data

    #check if DB is updated
    new_topic = db.session.scalars(sqla.select(ResearchTopic).where(ResearchTopic.topic_name == 'Robotics in Medicine')).first()
    assert new_topic is not None
    all_topics = db.session.scalars(sqla.select(ResearchTopic)).all()
    assert len(all_topics) == 4

    new_lang = db.session.scalars(sqla.select(ProgrammingLanguage).where(ProgrammingLanguage.lang_name == 'Ruby on Rails')).first()
    assert new_lang is not None
    all_langs = db.session.scalars(sqla.select(ProgrammingLanguage)).all()
    assert len(all_langs) == 4

    new_major = db.session.scalars(sqla.select(Major).where(Major.name == 'BME')).first()
    assert new_major is not None
    assert new_major.department == "Biomedical Engineering"
    all_majors = db.session.scalars(sqla.select(Major)).all()
    assert len(all_majors) == 6

    scooby = db.session.scalars(sqla.select(Faculty).where(Faculty.firstname == "Scooby")).first()
    response = test_client.post('/faculty/edit-lists/courses',
                                data=dict(new_major=new_major.id, new_num=1001, new_title="BioWeapons and You", new_faculty=scooby.id, submit = "Add"),
                                follow_redirects = True)

    assert response.status_code == 200
    new_course = db.session.scalars(sqla.select(Course).where(Course.title == "BioWeapons and You")).first()
    assert new_course is not None
    all_courses = db.session.scalars(sqla.select(Course)).all()
    assert len(all_courses) == 1

    #Try removing the newly added elements
    response = test_client.post('/faculty/edit-lists/delete',
                               data=dict(topics = [str(new_topic.topic_id)], languages = [str(new_lang.lang_id)], majors = [str(new_major.id)], courses = [str(new_course.id)],
                                          submit = "Delete"),
                          follow_redirects = True)
    assert response.status_code == 200

    all_topics = db.session.scalars(sqla.select(ResearchTopic)).all()
    #total number of topics should now be 3
    assert len(all_topics) == 3
    #total number of langs should now be 3
    all_langs = db.session.scalars(sqla.select(ProgrammingLanguage)).all()
    assert len(all_langs) == 3
    #total number of majors should now be 5
    all_majors = db.session.scalars(sqla.select(Major)).all()
    assert len(all_majors) == 5
    #total number of courses should now be 0
    all_courses = db.session.scalars(sqla.select(Course)).all()
    assert len(all_courses) == 0

    do_logout(test_client, path = '/faculty/logout')

def test_remove_associated_elements(request,test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/edit-lists' page is requested (POST)
    THEN check that users cannot delete elements that are already associated with a student's profile
    """

    #associate student with research topic and programming language
    stud = db.session.scalars(sqla.select(Student).where(Student.username == 'bob')).first()
    topic = db.session.scalars(sqla.select(ResearchTopic).where(ResearchTopic.topic_name == "Machine Learning")).first()
    lang = db.session.scalars(sqla.select(ProgrammingLanguage).where(ProgrammingLanguage.lang_name == "Python")).first()
    lang2 = db.session.scalars(sqla.select(ProgrammingLanguage).where(ProgrammingLanguage.lang_name == "Java")).first()
    stud.topics_of_interest.add(topic)
    stud.languages_known.add(lang2)
    db.session.commit()

    do_login(test_client, path = '/faculty/login', username = 'scooby', passwd = '123')

    #Try removing the newly added elements
    response = test_client.post('/faculty/edit-lists/delete',
                               data=dict(topics = [str(topic.topic_id)], languages = [str(lang.lang_id), str(lang2.lang_id)],
                                          submit = "Delete"),
                          follow_redirects = True)

    assert response.status_code == 200
    assert b"Remove Elements" in response.data
    topics = db.session.scalars(sqla.select(ResearchTopic)).all()
    for t in topics:
        assert b"Java" in response.data
    assert b"Add Elements" in response.data
    assert b"Could not delete topic &#39;Machine Learning&#39;: students with topic exist." in response.data
    assert b"Could not delete language &#39;Java&#39;: students with language exist." in response.data

    #check that Python was deleted from db
    lang = db.session.scalars(sqla.select(ProgrammingLanguage).where(ProgrammingLanguage.lang_name == "Python")).first()
    assert lang is None

    #check that Java was not deleted from db
    lang = db.session.scalars(sqla.select(ProgrammingLanguage).where(ProgrammingLanguage.lang_name == "Java")).first()
    assert lang is not None

    #check that Machine Learning was not deleted from db
    topic = db.session.scalars(sqla.select(ResearchTopic).where(ResearchTopic.topic_name == "Machine Learning")).first()
    assert topic is not None

    do_logout(test_client, path = '/faculty/logout')

def test_faculty_profile(request,test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/faculty/profile' page is requested (GET)
    THEN check that the response is valid
    """

    #check when user not logged in
    response = test_client.get('/faculty/profile', follow_redirects = True)
    response.status_code == 200
    assert b"Please log in to access this page" in response.data
    assert b"Welcome to ResearchConnect!" in response.data

    #check when logged in
    do_login(test_client, path = '/faculty/login', username = 'scooby', passwd = '123')
    response = test_client.get('/faculty/profile', follow_redirects = True)
    assert b"Faculty username: scooby" in response.data
    assert b"Edit your profile" in response.data

    do_logout(test_client, path = '/faculty/logout')

def test_faculty_edit_profile(request,test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/faculty/profile/edit' page is requested (GET, POST)
    THEN check that the response is valid
    """
    #check when user not logged in
    response = test_client.get('/faculty/profile/edit', follow_redirects = True)
    response.status_code == 200
    assert b"Please log in to access this page" in response.data
    assert b"Welcome to ResearchConnect!" in response.data

    do_login(test_client, path = '/faculty/login', username = 'scooby', passwd = '123')
    #edit username and password
    response = test_client.post('faculty/profile/edit', data = dict(username = 'scooby2', password = "321",
        password_check = "321", submit = "Save changes"), follow_redirects = True)
    assert response.status_code == 200
    assert b"scooby2" in response.data

    #check if db is updated
    prof_scooby_old = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).all()
    assert len(prof_scooby_old) == 0

    prof_scooby_new = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby2')).all()
    assert len(prof_scooby_new) == 1

    do_logout(test_client, path = '/faculty/logout')

def test_faculty_my_positions(request,test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/faculty/position/mypositions' page is requested (GET, POST)
    THEN check that the response is valid
    """
    #check page when no positions have been posted
    do_login(test_client, path = '/faculty/login', username = 'scooby', passwd = '123')
    response = test_client.get('/position/mypositions', follow_redirects = True)
    assert response.status_code == 200
    assert b"Faculty member has not posted any positions" in response.data
    do_logout(test_client, path = '/faculty/logout')

    #add position to db and associate with faculty member scooby
    f1 = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).first()
    p1 = ResearchPosition(
    position_title="RBE Research Assistant",
    description = "Assist with RBE research at least 16 hours per week",
    start_date=date(2025, 3, 14),
    end_date=date(2026, 3, 14),
    team_size=2,
    min_gpa = 3.7,
    advisor_id = f1.get_id(),
    reference_required = True)
    db.session.add(p1)
    db.session.commit()

    assert f1.positions_posted is not None
    do_login(test_client, path = '/faculty/login', username = 'scooby', passwd = '123')
    response = test_client.get('/position/mypositions', follow_redirects = True)
    assert response.status_code == 200
    assert b"Posted positions:" in response.data
    assert b"RBE Research Assistant" in response.data
    assert b"2" in response.data
    do_logout(test_client, path = '/faculty/logout')

def test_reference_requests(request,test_client, init_database):
   """
   GIVEN a Flask application configured for testing
   WHEN the '/faculty/requests/<application_id>/accept' page is requested (GET, POST)
   THEN check that the response is valid
   """
   #create an application
   f1 = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).first()
   db.session.add(f1)
   db.session.commit()


   p1 = ResearchPosition(
   position_title="RBE Research Assistant",
   description = "Assist with RBE research at least 16 hours per week",
   start_date=date(2025, 3, 14),
   end_date=date(2026, 3, 14),
   team_size=2,
   min_gpa = 3.7,
   advisor_id = f1.get_id(),
   reference_required = True)
   db.session.add(p1)
   db.session.commit()


   stud1 = db.session.scalars(sqla.select(Student).where(Student.username == "bob")).first()
   db.session.add(stud1)
   db.session.commit()
   app1 = Application(statement="I think I would be a good fit for this position.",
                  position = p1,
                  applicant = stud1,
                  faculty_ref = f1,
                  reference_status = Status.PENDING)

   db.session.add(app1)
   db.session.commit()


   #view all requests
   do_login(test_client, path = '/faculty/login', username = 'scooby', passwd = '123')
   response = test_client.get('/faculty/requests', follow_redirects = True)
   assert response.status_code == 200
   assert b"Reference Requests" in response.data
   assert b"Bob Dylan" in response.data
   assert b"Awaiting approval" in response.data

   #check if db is updated
   requests = f1.get_ref_requests()
   assert len(requests) == 1

   do_logout(test_client, path = '/faculty/logout')

def test_deny_request(request,test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/faculty/requests/<application_id>/accept' page is requested (GET, POST)
    THEN check that the response is valid
    """

    #create an application
    f1 = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).first()
    db.session.add(f1)
    db.session.commit()


    p1 = ResearchPosition(
    position_title="RBE Research Assistant",
    description = "Assist with RBE research at least 16 hours per week",
    start_date=date(2025, 3, 14),
    end_date=date(2026, 3, 14),
    team_size=2,
    min_gpa = 3.7,
    advisor_id = f1.get_id(),
    reference_required = True)
    db.session.add(p1)
    db.session.commit()


    stud1 = db.session.scalars(sqla.select(Student).where(Student.username == "bob")).first()
    db.session.add(stud1)
    db.session.commit()
    app1 = Application(statement="I think I would be a good fit for this position.",
                  position = p1,
                  applicant = stud1,
                  faculty_ref = f1,
                  reference_status = Status.PENDING)

    db.session.add(app1)
    db.session.commit()

    do_login(test_client, path = '/faculty/login', username = 'scooby', passwd = '123')
    response = test_client.get('/faculty/requests', follow_redirects = True)
    assert response.status_code == 200
    assert b"Reference Requests" in response.data
    assert b"Bob Dylan" in response.data
    assert b"Awaiting approval" in response.data

    req = db.session.scalars(f1.ref_requests.select()).first()
    response = test_client.post(f"/faculty/requests/{req.application_id}/deny",
                               data=dict(submit = "Deny"),
                          follow_redirects = True)
    assert b"Reference request rejected." in response.data

    response = test_client.get('/faculty/profile', follow_redirects = True)
    assert response.status_code == 200
    assert b"Reference Requests" in response.data

    assert b"Bob Dylan" in response.data
    assert b"Not Recommended" in response.data

    #check if db is updated
    assert app1.reference_status == Status.REJECTED
    do_logout(test_client, path = '/faculty/logout')

def test_approve_request(request,test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/faculty/requests/<application_id>/accept' page is requested (GET, POST)
    THEN check that the response is valid
    """

    #create an application
    f1 = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).first()
    db.session.add(f1)
    db.session.commit()


    p1 = ResearchPosition(
    position_title="RBE Research Assistant",
    description = "Assist with RBE research at least 16 hours per week",
    start_date=date(2025, 3, 14),
    end_date=date(2026, 3, 14),
    team_size=2,
    min_gpa = 3.7,
    advisor_id = f1.get_id(),
    reference_required = True)
    db.session.add(p1)
    db.session.commit()


    stud1 = db.session.scalars(sqla.select(Student).where(Student.username == "bob")).first()
    db.session.add(stud1)
    db.session.commit()
    app1 = Application(statement="I think I would be a good fit for this position.",
                  position = p1,
                  applicant = stud1,
                  faculty_ref = f1,
                  reference_status = Status.PENDING)

    db.session.add(app1)
    db.session.commit()

    do_login(test_client, path = '/faculty/login', username = 'scooby', passwd = '123')
    response = test_client.get('/faculty/requests', follow_redirects = True)
    assert response.status_code == 200
    assert b"Reference Requests" in response.data
    assert b"Bob Dylan" in response.data
    assert b"Awaiting approval" in response.data

    req = db.session.scalars(f1.ref_requests.select()).first()
    response = test_client.post(f"/faculty/requests/{req.application_id}/accept",
                               data=dict(submit = "Approve"),
                          follow_redirects = True)
    assert b"Reference request approved." in response.data
    response = test_client.get('/faculty/profile', follow_redirects = True)
    assert response.status_code == 200
    assert b"Reference Requests" in response.data

    assert b"Bob Dylan" in response.data
    assert b"Recommended" in response.data

    #check if db is updated
    assert app1.reference_status == Status.APPROVED
    do_logout(test_client, path = '/faculty/logout')






#Pranav's Tests
#INSERT TESTS HERE

#Elliot's Tests

def test_view_app(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/position/<position_id>/<application_id>' page is requested (GET)
    THEN check that faculty can view application details
    """
    fac = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).first()
    stud = db.session.scalars(sqla.select(Student).where(Student.username == 'bob')).first()

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


    app = Application(applicant_id=stud.get_id(),position_id=pos.position_id, application_status=Status.PENDING, statement="TBD")
    db.session.add(app)
    db.session.commit()
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


    app = Application(applicant_id=stud.get_id(),position_id=pos.position_id, application_status=Status.PENDING, statement="TBD")
    db.session.add(app)
    db.session.commit()

    do_login(test_client, path='/faculty/login', username='scooby', passwd='123')
    response = test_client.get(f'/position/{pos.position_id}/{app.application_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Bob" in response.data or b"bob" in response.data
    do_logout(test_client, path='/faculty/logout')

def test_approve_app(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/position/<position_id>/<application_id>/approve' page is requested (POST)
    THEN check that faculty can approve applications
    """
    fac = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).first()
    stud = db.session.scalars(sqla.select(Student).where(Student.username == 'bob')).first()

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


    app = Application(applicant_id=stud.get_id(),position_id=pos.position_id, application_status=Status.PENDING, statement="TBD")
    db.session.add(app)
    db.session.commit()

    do_login(test_client, path='/faculty/login', username='scooby', passwd='123')
    response = test_client.post(f'/position/{pos.position_id}/{app.application_id}/approve',data=dict(submit="Approve"),follow_redirects=True)
    assert response.status_code == 200
    assert b"Application approved." in response.data
    do_logout(test_client, path='/faculty/logout')

def test_deny_app(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/position/<position_id>/<application_id>/deny' page is requested (POST)
    THEN check that faculty can deny applications
    """
    fac = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).first()
    stud = db.session.scalars(sqla.select(Student).where(Student.username == 'bob')).first()

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


    app = Application(applicant_id=stud.get_id(),position_id=pos.position_id, application_status=Status.PENDING, statement="TBD")
    db.session.add(app)
    db.session.commit()

    do_login(test_client, path='/faculty/login', username='scooby', passwd='123')
    response = test_client.post(
        f'/position/{pos.position_id}/{app.application_id}/deny',
        data=dict(submit="Deny"),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Application denied." in response.data
    do_logout(test_client, path='/faculty/logout')

def test_view_student_profile(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/faculty/<student_id>/profile' page is requested (GET)
    THEN check that faculty can view student profiles
    """
    stud = db.session.scalars(sqla.select(Student).where(Student.username == 'bob')).first()

    do_login(test_client, path='/faculty/login', username='scooby', passwd='123')
    response = test_client.get(f'/faculty/{stud.get_id()}/profile',follow_redirects=True)
    assert response.status_code == 200
    assert b"Bob" in response.data
    assert b"Dylan" in response.data
    do_logout(test_client, path='/faculty/logout')

def test_my_position_details(request, test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/positions/myposition/<position_id>' page is requested (GET)
    THEN check that position details are displayed correctly
    """
    fac = db.session.scalars(sqla.select(Faculty).where(Faculty.username == 'scooby')).first()
    stud = db.session.scalars(sqla.select(Student).where(Student.username == 'bob')).first()

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


    app = Application(applicant_id=stud.get_id(), position_id=pos.position_id, application_status=Status.PENDING, statement="TBD")
    db.session.add(app)
    db.session.commit()

    do_login(test_client, path='/faculty/login', username='scooby', passwd='123')
    response = test_client.get(f'/positions/myposition/{pos.position_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"ML Research Position" in response.data
    assert b"Work on machine learning" in response.data
    do_logout(test_client, path='/faculty/logout')

def test_post_position(request, test_client, init_database):
    major2 = db.session.scalars(sqla.select(Major).where(Major.name == "MATH")).first()
    lang2 = db.session.scalars(sqla.select(ProgrammingLanguage).where(ProgrammingLanguage.lang_name == "Java")).first()
    topic2 = db.session.scalars(sqla.select(ResearchTopic).where(ResearchTopic.topic_name == "Machine Learning")).first()
    do_login(test_client, path='/faculty/login', username='scooby', passwd='123')
    response = test_client.post(f'/faculty/postposition', data = dict(position_title="ML Research Position",
                            description="Work on machine learning",
                            start_date=date(2025, 5, 1),
                            end_date=date(2025, 12, 31),
                            team_size=3,
                            min_gpa=3.5,
                            reference_required = False,
                            preferred_majors = [str(major2.id)],
                            research_topics = [str(topic2.topic_id)],
                            required_languages = [str(lang2.lang_id)],
                            submit = "Post"), follow_redirects=True)
    assert response.status_code == 200
    print(response.data)
    assert b"ML Research Position" in response.data
    do_logout(test_client, path='/faculty/logout')

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

    do_login(test_client,'/faculty/login', "scooby", "123")
    r = test_client.get(f"/positions/myposition/{pos.position_id}/data")
    assert r.status_code == 200
    assert b"ML Research" in r.data
    do_logout(test_client, path='/faculty/logout')