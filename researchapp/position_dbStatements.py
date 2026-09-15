from app import db, create_app
from app.models.models import User, Course, Major, Student, CourseTaken, ResearchTopic, ProgrammingLanguage, ResearchPosition, Faculty, Application, Status
from config  import Config
from datetime import date

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
import os

if os.path.exists("research.db"):
    os.remove("research.db")
elif os.path.exists("researchapp/research.db"):
    os.remove("researchapp/research.db")

app = create_app()
app.app_context().push()

db.create_all()

# Add Majors
major1 = Major(name = 'CS', department = 'Computer Science')
db.session.add(major1)
major2 = Major(name = 'DS', department = 'Data Science')
db.session.add(major2)
major3 = Major(name = 'ME', department = 'Mechanical Engineering')
db.session.add(major3)
major4 = Major(name = 'RBE', department = 'Robotics Engineering')
db.session.add(major4)
major5 = Major(name = 'MATH', department = 'Mathematics')
db.session.add(major5)
db.session.commit()

# Add courses
c1 = Course(coursenum='3733',majorid = major1.id, title='Software Engineering') # course is associated with major1
db.session.add(c1)
c2 = Course(coursenum='3431',majorid = major2.id, title='Database Systems')     # course is associated with major2
db.session.add(c2)
c3 = Course(coursenum='1001',majorid = major5.id, title='Introduction to Robotics')     # course is associated with major5
db.session.add(c3)
db.session.commit()

#add topics
topic1 = ResearchTopic(topic_name="Machine Learning in Science")
db.session.add(topic1)
topic2 = ResearchTopic(topic_name="Deep Learning and Neural Nets")
db.session.add(topic2)
topic3 = ResearchTopic(topic_name="Unix-based Operating Systems")
db.session.add(topic3)

#add langs
lang1 = ProgrammingLanguage(lang_name = "Python")
db.session.add(lang1)
lang2 = ProgrammingLanguage(lang_name = "Java")
db.session.add(lang2)
lang3 = ProgrammingLanguage(lang_name = "C/C++")
db.session.add(lang3)

f1 = Faculty(firstname="Jane", lastname = "Smith", email="jsmith@gmail.com",username="jane", department = "RBE", user_type = "Faculty", activated=True)
f1.set_password('123')
db.session.add(f1)
db.session.commit()
print(f1)

f2 = Faculty(firstname="John", lastname = "Mayer", email="john@gmail.com",username="johnny", department = "CS", user_type = "Faculty", activated=True)
f2.set_password('123')
db.session.add(f2)
db.session.commit()
print(f2)

f3 = Faculty(firstname="Ritvik", lastname = "Garg", email="rit.g.garg@gmail.com", username="rit.g,garg@gmail.com", department = "CS", user_type = "Faculty", activated=False)
db.session.add(f3)
db.session.commit()

f4 = Faculty(firstname="Vanya", lastname = "Malik", email="vanyamalik750@gmail.com", username="vanyamalik750@gmail.com", department = "CS", user_type = "Faculty", activated=False)
db.session.add(f4)
db.session.commit()

#add positions
p1 = ResearchPosition(
    position_title="RBE Research Assistant",
    description = "Assist with RBE research at least 16 hours per week",
    start_date=date(2025, 3, 14),
    end_date=date(2026, 3, 14),
    team_size=2,
    min_gpa = 3.7,
    advisor_id = f1.get_id(),
    reference_required = True
)
db.session.add(p1)
db.session.commit()

p2= ResearchPosition(
    position_title="CS Research Assistant",
    description = "Assist with CS research at least 16 hours per week",
    start_date=date(2025, 2, 14),
    end_date=date(2026, 2, 14),
    team_size=2,
    min_gpa = 3.8,
    reference_required = False
)
db.session.add(p2)
db.session.commit()

p3= ResearchPosition(
    position_title="Data Science Research Assistant",
    description = "Assist with Data Science research at least 16 hours per week",
    start_date=date(2025, 2, 14),
    end_date=date(2026, 2, 14),
    team_size=1,
    min_gpa = 3.8,
    reference_required = True
)
db.session.add(p3)
db.session.commit()
f1.positions_posted.add(p3)
db.session.commit()

p1.preferred_majors.add(major4)
p1.preferred_majors.add(major1)
p1.programming_languages.add(lang1)
p1.required_courses.add(c1)
p1.required_courses.add(c2)
p1.research_topics.add(topic1)
p1.research_topics.add(topic2)
db.session.commit()

p2.preferred_majors.add(major4)
p2.preferred_majors.add(major5)
p2.programming_languages.add(lang1)
p2.programming_languages.add(lang2)
p2.programming_languages.add(lang3)
p2.required_courses.add(c2)
p2.required_courses.add(c3)
p2.research_topics.add(topic1)
p2.research_topics.add(topic2)
db.session.commit()

p3.preferred_majors.add(major1)
p3.preferred_majors.add(major2)
p3.programming_languages.add(lang2)
p3.programming_languages.add(lang3)
p3.required_courses.add(c3)
p3.research_topics.add(topic3)
p3.research_topics.add(topic2)
db.session.commit()

print(p1.get_preferred_majors())
print(p1.get_required_languages())
print(p1.get_required_courses())
print(p1.get_research_topics())

positions = db.session.scalars(sqla.select(ResearchPosition)).all()
for p in positions:
    print(p)


f1.positions_posted.add(p1)
f1.courses_taught.add(c1)
f1.positions_posted.add(p2)
db.session.commit()
f2.positions_posted.add(p2)
f2.courses_taught.add(c2)
f2.courses_taught.add(c3)
f2.positions_posted.add(p3)
db.session.commit()

faculty = db.session.scalars(sqla.select(Faculty)).all()
for f in faculty:
    print(f"position posted: {f.get_positions_posted()}")
    print(f"courses taught: {f.get_courses_taught()}")

stud1 = Student(firstname="Bob", lastname = "Dylan", email="bob@gmail.com",username="bob",
                wpi_id = "901013026", gpa = 3.8, user_type = "Student")
stud1.set_password("123")
stud1.majors_of_student.add(major1)
stud1.majors_of_student.add(major4)
stud1.topics_of_interest.add(topic1)
stud1.topics_of_interest.add(topic3)
stud1.languages_known.add(lang1)
stud1.languages_known.add(lang2)
db.session.add(stud1)
db.session.commit()

stud2 = Student(firstname="Will", lastname = "Ferrell", email="wferrell@gmail.com",username="will",
                wpi_id = "901014026", gpa = 3.5, user_type = "Student")
stud2.set_password("123")
stud2.majors_of_student.add(major2)
stud2.majors_of_student.add(major3)
stud2.topics_of_interest.add(topic1)
stud2.topics_of_interest.add(topic2)
stud2.languages_known.add(lang1)
stud2.languages_known.add(lang2)
db.session.add(stud2)
db.session.commit()

stud3 = Student(firstname="Morgan", lastname = "Shia", email="morganshia@wpi.edu",username="morgan",
                wpi_id = "901015026", gpa = 4.0, user_type = "Student")
stud3.set_password("123")
stud3.majors_of_student.add(major5)
stud3.topics_of_interest.add(topic2)
stud3.topics_of_interest.add(topic3)
stud3.languages_known.add(lang2)
stud3.languages_known.add(lang3)
db.session.add(stud3)
db.session.commit()

studs = db.session.scalars(sqla.select(Student)).all()
for stud in studs:
    print(stud)

ct_1 = CourseTaken(student_id=stud1.id, course_id=c1.id, course_name=c1.title, grade_recieved="A")
db.session.add(ct_1)
ct_2 = CourseTaken(student_id=stud2.id, course_id=c2.id, course_name=c2.title, grade_recieved="B")
db.session.add(ct_2)
ct_3 = CourseTaken(student_id=stud3.id, course_id=c3.id, course_name=c3.title, grade_recieved="NR")
db.session.add(ct_3)
db.session.commit()

#create applications for positions

stud1_app1 = Application(statement="I think I would be a good fit for this position.",
                   position = p1,
                   applicant = stud1,
                   faculty_ref = f2,
                   reference_status = Status.PENDING)

stud1_app2 = Application(statement="I think I would be a good fit for this position.",
                   position = p2,
                   applicant = stud1)

stud2_app1 = Application(statement="I am a good RBE student.",
                   position = p1,
                   applicant = stud2,
                   faculty_ref = f2,
                   reference_status = Status.PENDING)

stud2_app2 = Application(statement="IDK dude",
                    position = p2,
                    applicant = stud2,
                    reference_status = Status.PENDING)

stud3_app1 = Application(statement="IDK dude",
                    position = p1,
                    applicant = stud3,
                    faculty_ref = f3,
                    reference_status = Status.PENDING)

db.session.add(stud1_app1)
db.session.add(stud1_app2)
db.session.commit()
db.session.add(stud2_app1)
db.session.add(stud2_app2)
db.session.commit()
db.session.add(stud3_app1)
db.session.commit()
print(stud1_app1)
print(f"student 1 applications: {stud1.get_student_apps()}")
print(f"Reference status for stud1_app1: {stud1_app1.reference_status.value}")
print(f"Application status for stud1_app1: {stud1_app1.application_status.value}")
print(f"Application status for stud1_app2: {stud1_app2.application_status.value}")
print("Pending requests for f2:")
print(db.session.scalars(f2.ref_requests.select().where(Application.reference_status == Status.PENDING)).all())
stud1_app1.approve_reference()
stud1_app1.approve_application()
db.session.commit()
print(f"Reference status for stud1_app1: {stud1_app1.reference_status.value}")
print(f"Application status for stud1_app1: {stud1_app1.application_status.value}")
stud1_app2.reject_application()
db.session.commit()
print(f"Application status for stud1_app2: {stud1_app2.application_status.value}")

print(f"student 2 applications: {stud2.get_student_apps()}")
print(f"Reference status for stud2_app1: {stud2_app1.reference_status.value}")
stud2_app1.reject_reference()
stud2_app1.withdraw_application()
db.session.commit()
print(f"Reference status for stud2_app1: {stud2_app1.reference_status.value}")
print(f"Application status for stud2_app1: {stud2_app1.application_status.value}")

print(db.session.scalars(sqla.select(Faculty)).all())

# # Add couple students
# s1 = Student(username='vanya', firstname = 'Vanya', lastname = 'Malik', email='vmalik@wpi.edu', address = 'WPI')
# s1.set_password('123')
# db.session.add(s1)

# s2 = Student(username='john', firstname = 'John', lastname = 'Yates', email='john@wpi.edu', address = 'WPI')
# s2.set_password('123')
# db.session.add(s2)

# s3 = Student(username='kitten', firstname = 'Snow', lastname = 'Thecat', email='meow@wpi.edu', address = 'Cat Town')
# s3.set_password('123')
# db.session.add(s3)
# db.session.commit()

# # print students
# query = sqla.select(Student)
# results = db.session.scalars(query)
# for student in results:
#     print(student)

# # query Student
# s1 = db.session.scalars(sqla.select(Student).where(Student.username == 'sakire')).first()
# s2 = db.session.scalars(sqla.select(Student).where(Student.username == 'john')).first()
# s3 = db.session.scalars(sqla.select(Student).where(Student.username == 'kitten')).first()

# major1 = db.session.scalars(sqla.select(Major).where(Major.name == 'CS')).first()
# major2 = db.session.scalars(sqla.select(Major).where(Major.name == 'RBE')).first()

# #enrollment statements
# student = db.session.scalars(sqla.select(Student).where(Student.username == 'kitten')).first()
# major = db.session.scalars(sqla.select(Major).where(Major.name == 'CS')).first()
# course = db.session.scalars(sqla.select(Course).where(Course.majorid == major.id).where(Course.coursenum == '3733')).first()

# #check if student is enrolled in specific course
# is_enrolled = db.session.scalars(student.enrollments.select().where(Enrolled.course_id == course.id)).first()

# #get student's enrolled courses
# enrollments = db.session.scalars(student.enrollments.select()).all()

# #enroll a student
# new_enrollment = Enrolled(course_enrolled = course, student_enrolled = student)
# db.session.add(new_enrollment)
# db.session.commit()

# #unenroll a student
# current_enrollment = db.session.scalars(student.enrollments.select().where(Enrolled.course_id == course.id)).first()
# db.session.delete(current_enrollment)
# db.session.commit()



# # print majors of the student, i.e., CS and RBE
# for m in s1.get_majors():
#     print(m)

# # print students in the RBE major
# for s in major2.get_students():
#     print(s)

# #--------------------------------------------------
# # We will use the following statements in later videos

# # Add couple Majors
# major1 = Major(name = 'CS', department = 'Computer Science')
# db.session.add(major1)
# major2 = Major(name = 'DS', department = 'Computer Science')
# db.session.add(major2)
# major3 = Major(name = 'ME', department = 'Mechanical Engineering')
# db.session.add(major3)
# major4 = Major(name = 'RBE', department = 'Robotics Engineering')
# db.session.add(major4)
# major5 = Major(name = 'MATH', department = 'Mathematics')
# db.session.add(major5)
# db.session.commit()

# # print Courses
# query = sqla.select(Major)
# results = db.session.scalars(query)
# for major in results:
#     print(major)

# query =  sqla.select(Major).where(Major.name == 'CS')
# result = db.session.execute(query)
# major1 = result.scalars().first()
# # major1 = result.scalars().all()[0]

# query =  sqla.select(Major).where(Major.name == 'RBE')
# major2 = db.session.scalars(query).first()

# # Add couple courses
# c1 = Course(coursenum='3733',majorid = major1.id, title='Software Engineering') # course is associated with major1
# db.session.add(c1)
# c2 = Course(coursenum='3431',majorid = major1.id, title='Database Systems')     # course is associated with major1
# db.session.add(c2)
# c3 = Course(coursenum='1001',majorid = major2.id, title='Introduction to Robotics')     # course is associated with major2
# db.session.add(c3)
# db.session.commit()

# # Add couple students
# s1 = Student(username='sakire', firstname = 'Sakire', lastname = 'Arslan Ay', email='sakire@wpi.edu', address = 'WPI')
# s1.set_password('123')
# db.session.add(s1)

# s2 = Student(username='john', firstname = 'John', lastname = 'Yates', email='john@wpi.edu')  #address is optional
# s2.set_password('123')
# db.session.add(s2)

# s3 = Student(username='kitten', firstname = 'Snow', lastname = 'Thecat', email='meow@wpi.edu', address = 'Cat Town')  #address is optional
# s3.set_password('123')
# db.session.add(s3)
# db.session.commit()

# # print Courses
# query = sqla.select(Course)
# results = db.session.scalars(query)
# for course in results:
#     print(course)

# print("-----------------------------")
# # print courses for major1
# for course in major1.get_courses():
#     print(course)

# print("-----------------------------")
# # print students
# query = sqla.select(Student)
# results = db.session.scalars(query)
# for student in results:
#     print(student)



