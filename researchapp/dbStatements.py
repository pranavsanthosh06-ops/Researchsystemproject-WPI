from app import db, create_app
from app.models.models import User, Course, Major, Student, CourseTaken, ResearchTopic, ProgrammingLanguage, Faculty
from config  import Config

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
import os
os.remove("researchapp/research.db")

app = create_app()
app.app_context().push()

db.create_all()

user1 = User(firstname="Alex",lastname="Turner",email="alex@gmail.com",username="alex")
user1.set_password("123")
db.session.add(user1)
db.session.commit()

user2 = User(firstname="Frosty",lastname="Thesnowman",email="frosty@gmail.com",username="frosty")
user2.set_password("123")
db.session.add(user2)
db.session.commit()

users = db.session.scalars(sqla.select(User)).all()
for u in users:
    print(u)


# Add Majors
major1 = Major(name = 'CS', department = 'Computer Science')
db.session.add(major1)
major2 = Major(name = 'DS', department = 'Computer Science')
db.session.add(major2)
major3 = Major(name = 'ME', department = 'Mechanical Engineering')
db.session.add(major3)
major4 = Major(name = 'RBE', department = 'Robotics Engineering')
db.session.add(major4)
major5 = Major(name = 'MATH', department = 'Mathematics')
db.session.add(major5)
db.session.commit()

# print Majors
query = sqla.select(Major)
results = db.session.scalars(query)
for major in results:
    print(major)


# Add couple courses
c1 = Course(coursenum='3733',majorid = major1.id, title='Software Engineering') # course is associated with major1
db.session.add(c1)
c2 = Course(coursenum='3431',majorid = major1.id, title='Database Systems')     # course is associated with major1
db.session.add(c2)
c3 = Course(coursenum='1001',majorid = major2.id, title='Introduction to Robotics')     # course is associated with major2
db.session.add(c3)
db.session.commit()

query = sqla.select(Course)
results = db.session.scalars(query)
for course in results:
    print(course)

stud1 = Student(firstname="Bob", lastname = "Dylan", email="bob@gmail.com",username="bob",
                wpi_id = "901013026", gpa = 3.8, user_type = "Student")
stud1.set_password("123")
db.session.add(stud1)
db.session.commit()

stud2 = Student(firstname="Ferris", lastname = "Bueller", email="ferris@gmail.com",username="ferris",
                wpi_id = "901014026", gpa = 3.5, user_type = "Student")
stud2.set_password("123")
db.session.add(stud2)
db.session.commit()

stud3 = Student(firstname="Santa", lastname = "Claus", email="santa@northpole.com",username="santa",
                wpi_id = "901015026", gpa = 4.0, user_type = "Student")
stud3.set_password("123")
db.session.add(stud3)
db.session.commit()

studs = db.session.scalars(sqla.select(Student)).all()
for stud in studs:
    print(stud)

# associate the Students with Majors  (Many-to-Many relationship through 'students_majors_table' association table)
stud1.majors_of_student.add(major1)
stud1.majors_of_student.add(major2)
stud2.majors_of_student.add(major2)
stud3.majors_of_student.add(major3)
db.session.commit()

for stud in studs:
    print(stud.get_majors())

stud1.add_taken_course(c1, 'A')
stud1.add_taken_course(c2, 'B')
stud2.add_taken_course(c1, 'B')
stud2.add_taken_course(c3, 'B')
stud3.add_taken_course(c3, 'A')

for stud in studs:
    print(stud.get_firstname(), stud.taken_courses())

topic1 = ResearchTopic(topic_name="Machine Learning in Science")
db.session.add(topic1)
topic2 = ResearchTopic(topic_name="Deep Learning and Neural Nets")
db.session.add(topic2)
topic3 = ResearchTopic(topic_name="Unix-based Operating Systems")
db.session.add(topic3)
stud1.topics_of_interest.add(topic1)
stud1.topics_of_interest.add(topic2)
stud2.topics_of_interest.add(topic1)
stud3.topics_of_interest.add(topic3)

for stud in studs:
    print(stud.get_interested_topics())

lang1 = ProgrammingLanguage(lang_name = "Python")
db.session.add(lang1)
lang2 = ProgrammingLanguage(lang_name = "Java")
db.session.add(lang2)
lang3 = ProgrammingLanguage(lang_name = "C/C++")
db.session.add(lang3)
stud1.languages_known.add(lang1)
stud1.languages_known.add(lang2)
stud2.languages_known.add(lang3)
stud3.languages_known.add(lang2)
f1 = Faculty(firstname="Scooby", lastname = "Doo", email="scooby@gmail.com",username="scooby", department = "RBE", user_type = "Faculty")
db.session.add(f1)
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

for stud in studs:
    print(stud.get_programming_languages())

print(f"Students that know Lang3: {db.session.scalars(lang3.students.select()).all()}.")

print(f"all topics: {db.session.scalars(sqla.select(ResearchTopic)).all()}")

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



