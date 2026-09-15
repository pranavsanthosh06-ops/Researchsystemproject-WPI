from app import db, mail
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla
from app.models.models import Course, Student, ResearchPosition, CourseTaken, Application, Status, student_decorator
from app.studmain.forms import CourseForm, EditForm, EmptyForm, ApplicationFormWithRef, ApplicationForm
from flask_login import current_user
from flask_mail import Message

from app.studmain import studentmain_blueprint as smain

@smain.route('/', methods=['GET'])
@smain.route('/welcome', methods=['GET'])
def main():
    if current_user.is_authenticated:
        if current_user.get_user_type() == "Student":
            return redirect(url_for('studentmain.index'))
        elif current_user.get_user_type() == "Faculty":
            return redirect(url_for('facultymain.mypositions'))
        else:
            flash('fatal error has occurred')
    return render_template('welcome.html')


@smain.route('/index', methods=['GET'])
@student_decorator
def index():
    empty_form = EmptyForm()
    query = sqla.select(Course)
    courses = db.session.scalars(query)
    students = db.session.scalars(sqla.select(Student))
    positions = db.session.scalars(sqla.select(ResearchPosition))
    return render_template('index.html', title="Course List", all_positions = positions, courses=courses, students = students, recommended = False, form = empty_form)

@smain.route('/positions/recommended', methods=['GET'])
@student_decorator
def recommended_positions():
    empty_form = EmptyForm()
    positions = db.session.scalars(sqla.select(ResearchPosition))
    courses = db.session.scalars(sqla.select(Course))
    positions_scores = []
    for pos in positions:
        score = 0
        pos_majors = pos.get_preferred_majors()
        pos_topics = pos.get_research_topics()
        pos_courses = pos.get_required_courses()
        pos_langs = pos.get_required_languages()
        for m in pos_majors:
            if m in current_user.get_majors():
                score += 2
        for t in pos_topics:
            if t in current_user.get_interested_topics():
                score += 3  
        for course in pos_courses:
            if current_user.in_courses(course):
                score += 3
        for l in pos_langs:
            if l in current_user.get_programming_languages():
                score += 4 #programming languages have the most weight
        positions_scores.append((pos, score))
    
    positions_scores.sort(key = lambda x : x[1], reverse = True)
    ranked_positions = []
    for p, s in positions_scores:
        ranked_positions.append(p)
    return render_template('index.html', title="Course List", all_positions = ranked_positions, courses=courses, recommended = True, form = empty_form)

@smain.route("/positions/<position_id>", methods=['GET'])
def position_details(position_id):
    position = db.session.get(ResearchPosition, position_id)
    if position is None:
        flash("Research position not found.")
        return redirect(url_for('studentmain.index'))
    return render_template("position_details.html", title="Position Details", position=position)

@smain.route("/positions/<position_id>/data", methods = ['GET'])
@student_decorator
def position_data(position_id):
    theposition = db.session.get(ResearchPosition, position_id)
    topics = theposition.get_research_topics()
    topic_names = []
    for t in topics:
        topic_names.append(t.topic_name)

    langs = theposition.get_required_languages()
    lang_names = []
    for l in langs:
        lang_names.append(l.lang_name)
    
    courses = theposition.get_required_courses()
    course_names = []
    for c in courses:
        course_names.append(c.title)
    
    majors = theposition.get_preferred_majors()
    major_names = []
    for m in majors:
        major_names.append(m.name)

    data = {'position_title': theposition.position_title,
            'advisor': theposition.get_advisor_name(),
            'description': theposition.description,
            'topics': topic_names,
            'languages' : lang_names,
            'courses' : course_names,
            'majors' : major_names}
    
    return jsonify(data)

@smain.route('/course/create', methods=['GET', 'POST'])
@student_decorator
def addclass():
    cForm = CourseForm()
    if cForm.title.data and cForm.validate_on_submit(): #returns true only if there is a post request recieved and if all data in the form is validated
        new_class = cForm.title.data
        grade_recieved = cForm.grade_recieved.data
        current_user.add_taken_course(new_class, grade_recieved)
        flash('Course "' + new_class.title + '" is added')
        return redirect(url_for('studentmain.display_profile')) #returns url of endpoint for this function
    return render_template("add_course.html", form = cForm)


@smain.route("/student/profile", methods = ['GET'])
@student_decorator
def display_profile():
    emptyform = EmptyForm()
    return render_template('display_profile.html', title = 'Display Profile', student = current_user, form=emptyform)

@smain.route("/student/editprofile", methods = ['GET', 'POST'])
@student_decorator
def edit_profile():
    eForm = EditForm()
    if request.method =='POST':
        if eForm.validate_on_submit():
            current_user.username = eForm.username.data
            current_user.firstname = eForm.firstname.data
            current_user.lastname = eForm.lastname.data
            current_user.email = eForm.email.data
            current_user.wpi_id = eForm.wpi_id.data
            current_user.gpa = eForm.gpa.data
            current_user.set_password(eForm.password.data)

            for major in current_user.get_majors():
                current_user.majors_of_student.remove(major)

            for major in eForm.majors.data:
                current_user.majors_of_student.add(major)

            for topic in current_user.get_interested_topics():
                current_user.topics_of_interest.remove(topic)

            for topic in eForm.research_topics.data:
                current_user.topics_of_interest.add(topic)

            for lang in current_user.get_programming_languages():
                current_user.languages_known.remove(lang)

            for lang in eForm.programming_languages.data:
                current_user.languages_known.add(lang)

            db.session.add(current_user)
            db.session.commit()
            flash("Your changes have been made")
            return redirect(url_for('studentmain.display_profile'))
        else:
            print("Form not validated") #debugging purposes
    elif request.method == 'GET':
    #populate form data from the DB
        eForm.username.data = current_user.username
        eForm.firstname.data = current_user.firstname
        eForm.lastname.data = current_user.lastname
        eForm.email.data = current_user.email
        eForm.wpi_id.data = current_user.wpi_id
        eForm.gpa.data = current_user.gpa


        for major in current_user.get_majors():
            eForm.majors.data.append(major)
        for topic in current_user.get_interested_topics():
            eForm.research_topics.data.append(topic)
        for lang in current_user.get_programming_languages():
            eForm.programming_languages.data.append(lang)

    else:
        pass
    return render_template('edit_profile.html', title = 'Edit Profile', form = eForm)


@smain.route("/course/<course_taken_id>/delete", methods = ['POST'])
@student_decorator
def delete(course_taken_id):
    thecourse = db.session.get(CourseTaken, course_taken_id)
    if thecourse is None:
        flash("Course with specified ID {} not found".format(course_taken_id))
        return redirect(url_for('studentmain.index'))
    current_user.remove_taken_course(thecourse)
    flash("You deleted a course")
    return redirect(url_for('studentmain.display_profile'))





def send_ref_notification(recipient: str):
    """
    Creates and sends a verification email to given recipient.

    Parameters:
        recipient (str): email of the recipient

    Returns:
        str: verification code sent to the recipient
    """
    body_string: str = "The student {} {} has submitted a reference request. Please visit your ResearchConnect dashboard to view.".format(current_user.firstname, current_user.lastname)
    msg = Message(
        subject='You have a new reference request',
        recipients=[recipient],
        body=body_string
    )
    mail.send(msg)

@smain.route("/positions/<position_id>/apply", methods=['GET', 'POST'])
@student_decorator
def apply_position(position_id):
    research_position = db.session.get(ResearchPosition, position_id)
    if research_position is None:
        flash("Research position not found.")
        return redirect(url_for('studentmain.index'))
    if current_user.has_applied(position_id):
        flash("You have already applied to this position")
        return redirect(url_for('studentmain.index'))

    if research_position.reference_required:
        aform = ApplicationFormWithRef(research_position)
        if aform.validate_on_submit():
            new_app = Application(statement = aform.statement.data,
                                  faculty_ref = aform.faculty_ref.data,
                                  applicant = current_user,
                                  reference_status = Status.PENDING,
                                  position = research_position)
            db.session.add(new_app)
            db.session.commit()
            faculty_ref = aform.faculty_ref.data
            send_ref_notification(faculty_ref.email)
            flash("Reference request has been sent to faculty member")
            flash("Application submitted")
            return redirect(url_for("studentmain.index"))
    else:
        aform = ApplicationForm()
        if aform.validate_on_submit():
            new_app = Application(statement = aform.statement.data,
                                  applicant = current_user,
                                  position = research_position)
            db.session.add(new_app)
            db.session.commit()
            flash("Application submitted")
            return redirect(url_for("studentmain.index"))
    return render_template("apply_position.html", form = aform, position=research_position)

@smain.route("/applications/<application_id>/view", methods=['GET'])
@student_decorator
def view_application(application_id):
    application = db.session.get(Application, application_id)
    return render_template("view_application.html", application = application)

@smain.route("/applications", methods=['GET'])
@student_decorator
def view_all_applications():
    apps = current_user.get_student_apps()
    return render_template("my_applications.html", applications=apps)

@smain.route('/applications/<int:application_id>/withdraw', methods=['POST'])
@student_decorator
def withdraw_application(application_id):
    application = db.session.get(Application, application_id)

    if application is None or application.applicant_id != current_user.id:
        flash("Application not found.")
        return redirect(url_for('studentmain.view_all_applications'))

    if application.application_status.value != "Pending":
        flash("Only pending applications can be withdrawn.")
        return redirect(url_for('studentmain.view_all_applications'))

    application.application_status = Status.WITHDRAWN
    db.session.commit()

    flash("Application withdrawn.")
    return redirect(url_for('studentmain.view_all_applications'))
