from app import db, create_app
from config import Config
from app.models.models import User, Course, Major, Student, ResearchTopic, ProgrammingLanguage, Faculty, ResearchPosition
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from flask_login import current_user
from datetime import datetime, timezone, date

app = create_app(Config)

# @app.shell_context_processor
# def make_shell_context():
#     return {'sqla': sqla, 'sqlo': sqlo, 'db': db, 'Course': Course, 'Student' : Student}


@sqla.event.listens_for(Major.__table__, "after_create")
def add_majors(*args, **kwargs):
    query = sqla.select(Major)
    if db.session.scalars(query).first() is None:
        majors = [{'name':'CS','department':'Computer Science'},
          {'name':'DS','department':'Computer Science'},
          {'name':'RBE','department':'Robotics Engineering'},
          {'name':'ME','department':'Mechanical Engineering'},
          {'name':'MATH','department': 'Mathematics'}  ]
        for major in majors:
            db.session.add(Major(name = major['name'], department = major['department']))
        db.session.commit()

# @sqla.event.listens_for(Faculty.__table__, "after_create")
# def add_majors(*args, **kwargs):
#     query = sqla.select(Faculty)
#     if db.session.scalars(query).first() is None:
#             f1 = Faculty(firstname="Scooby", lastname = "Doo", email="scooby@gmail.com",username="scooby", department = "RBE", user_type = "Faculty")
#             db.session.add(f1)
#             f2 = Faculty(firstname="John", lastname = "Mayer", email="john@gmail.com",username="johnny", department = "CS", user_type = "Faculty")
#             db.session.add(f2)
#             db.session.commit()

# @sqla.event.listens_for(Course.__table__, "after_create")
# def add_majors(*args, **kwargs):
#     query = sqla.select(Course)
#     if db.session.scalars(query).first() is None:
#             c1 = Course(coursenum='3733', title='Software Engineering') # course is associated with major1
#             db.session.add(c1)
#             c2 = Course(coursenum='3431', title='Database Systems')     # course is associated with major1
#             db.session.add(c2)
#             c3 = Course(coursenum='1001', title='Introduction to Robotics')     # course is associated with major2
#             db.session.add(c3)
#             db.session.commit()

@sqla.event.listens_for(db.metadata, "after_create")
def add_courses(*args, **kwargs):
    query = sqla.select(Course)
    if db.session.scalars(query).first() is None:
            c1 = Course(coursenum='3733', title='Software Engineering', majorid = 1) # course is associated with major1
            db.session.add(c1)
            c2 = Course(coursenum='3431', title='Database Systems', majorid = 1)     # course is associated with major1
            db.session.add(c2)
            c3 = Course(coursenum='1001', title='Introduction to Robotics', majorid = 3)     # course is associated with major2
            db.session.add(c3)
            db.session.commit()

            query2 = sqla.select(Faculty)
            if db.session.scalars(query2).first() is None:
                f1 = Faculty(firstname="Scooby", lastname = "Doo", email="scooby@gmail.com",username="scooby", department = "RBE", user_type = "Faculty", activated = True)
                db.session.add(f1)
                db.session.commit()
                print(f1)
                f2 = Faculty(firstname="John", lastname = "Mayer", email="john@gmail.com",username="johnny", department = "CS", user_type = "Faculty", activated = True)
                db.session.add(f2)
                db.session.commit()
                f1.courses_taught.add(c1)
                db.session.add(f1)
                db.session.commit()
                f1.courses_taught.add(c2)
                db.session.add(f1)
                db.session.commit()
                f1.courses_taught.add(c3)
                db.session.add(f1)
                db.session.commit()
                db.session.commit()


@sqla.event.listens_for(ProgrammingLanguage.__table__, "after_create")
def add_langs(*args, **kwargs):
    query = sqla.select(ProgrammingLanguage)
    if db.session.scalars(query).first() is None:
        langs = ['Java', 'Python', 'C/C++']
        for lang in langs:
            db.session.add(ProgrammingLanguage(lang_name = lang))
        db.session.commit()
        db.session.scalars(sqla.select(ProgrammingLanguage)).all()

@sqla.event.listens_for(ResearchTopic.__table__, "after_create")
def add_langs(*args, **kwargs):
    query = sqla.select(ResearchTopic)
    if db.session.scalars(query).first() is None:
        topics = ['Advnaced Machine Learning', 'Unix-based Operating Systems', 'Mechanical Robots']
        for topic in topics:
            db.session.add(ResearchTopic(topic_name = topic))
        db.session.commit()

@app.before_request
def initDB(*args, **kwargs):
    if app._got_first_request:
        db.create_all()

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.add(current_user)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True, port=3000)

