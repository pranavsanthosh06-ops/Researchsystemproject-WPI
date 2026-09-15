from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla
from app.models.models import ResearchTopic, ProgrammingLanguage, ResearchPosition, Application, Student, Course, Major, faculty_decorator, Status
from app.facultymain.facultyforms import DeleteListsForm, AddListsForm, AddCourseForm, EditForm, PostPositionForm, EmptyForm, ApproveForm, DenyForm
from flask_login import current_user
from sqlalchemy import text

from app.facultymain import facultymain_blueprint as fmain

@fmain.route('/faculty/edit-lists', methods=['GET', 'POST'])
@faculty_decorator
def edit_lists():
    dlForm = DeleteListsForm()
    alForm = AddListsForm()
    aForm = AddCourseForm()
    return render_template('edit_lists.html', dlform = dlForm, alform = alForm, form = aForm)

@fmain.route('/faculty/edit-lists/delete', methods=['POST'])
@faculty_decorator
def delete_lists():
    dlForm = DeleteListsForm()
    alForm = AddListsForm()
    aForm = AddCourseForm()
    if dlForm.submit.data and dlForm.validate():
        selected: bool = False
        majors_removed: int = 0
        courses_removed: int = 0
        topics_removed: int = 0
        langs_removed: int = 0
        for course in dlForm.courses.data:
            if len(course.get_students()) > 0:
                flash("Could not delete course '" + course.to_string() + "': students with course exist.")
            else:
                courses_removed += 1
                db.session.delete(course)
                db.session.commit()
            selected = True
        for major in dlForm.majors.data:
            if len(major.get_courses()) > 0:
                flash("Could not delete major '" + major.to_string() + "': courses with major exist.")
            elif len(major.get_students()) > 0:
                flash("Could not delete major '" + major.to_string() + "': students with major exist.")
            else:
                majors_removed += 1
                db.session.delete(major)
                db.session.commit()
            selected = True
        for topic in dlForm.topics.data:
            if len(topic.students_with_topic()) > 0:
                flash("Could not delete topic '" + topic.to_string() + "': students with topic exist.")
            else:
                topics_removed += 1
                db.session.delete(topic)
                db.session.commit()
            selected = True
        for lang in dlForm.languages.data:
            if len(lang.students_with_lang()) > 0:
                flash("Could not delete language '" + lang.to_string() + "': students with language exist.")
            else:
                langs_removed += 1
                db.session.delete(lang)
                db.session.commit()
            selected = True
        if not selected:
            flash("No data selected.")
        elif majors_removed != 0 or courses_removed != 0 or topics_removed != 0 or langs_removed != 0:
            flash("Data removed.")
        return redirect(url_for('facultymain.edit_lists'))
    return render_template('edit_lists.html', dlform = dlForm, alform = alForm, form = aForm)

@fmain.route('/faculty/edit-lists/add', methods=['POST'])
@faculty_decorator
def add_lists():
    dlForm = DeleteListsForm()
    alForm = AddListsForm()
    aForm = AddCourseForm()
    if alForm.submit.data and alForm.validate():
        changed: bool = False
        if not (alForm.new_major_name.data == "" or alForm.new_major_dept.data == ""):
            new_major = Major(
                name = alForm.new_major_name.data,
                department = alForm.new_major_dept.data
            )
            db.session.add(new_major)
            db.session.commit()
            alForm.new_major_name = ""
            alForm.new_major_dept = ""
            changed = True
        if not alForm.new_topic.data == "":
            new_topic = ResearchTopic(
                topic_name = alForm.new_topic.data
            )
            db.session.add(new_topic)
            db.session.commit()
            alForm.new_topic.data = ""
            changed = True
        if not alForm.new_lang.data == "":
            new_lang = ProgrammingLanguage(
                lang_name = alForm.new_lang.data
            )
            db.session.add(new_lang)
            db.session.commit()
            alForm.new_lang.data = ""
            changed = True
        if changed:
            flash("Data added.")
        else:
            flash("No data selected.")
        return redirect(url_for('facultymain.edit_lists'))
    return render_template('edit_lists.html', dlform = dlForm, alform = alForm, form = aForm)

@fmain.route("/faculty/edit-lists/courses", methods=['POST'])
@faculty_decorator
def add_courses():
    dlForm = DeleteListsForm()
    alForm = AddListsForm()
    aForm = AddCourseForm()
    if aForm.validate_on_submit():
        new_course = Course(
            majorid = aForm.new_major.data.id,
            coursenum = str(aForm.new_num.data),
            title = aForm.new_title.data
        )
        aForm.new_faculty.data.courses_taught.add(new_course)
        db.session.add(new_course)
        db.session.commit()
        flash("Course added.")
        return redirect(url_for('facultymain.edit_lists'))
    return render_template('edit_lists.html', dlform = dlForm, alform = alForm, form = aForm)

@fmain.route("/faculty/profile", methods = ['GET'])
@faculty_decorator
def display_profile():
    references = current_user.get_ref_requests()
    aform = ApproveForm()
    dform = DenyForm()
    return render_template('faculty_display_profile.html', title='Display Profile', faculty=current_user, references = references, aform = aform, dform = dform)

@fmain.route("/faculty/profile/edit", methods = ['GET', 'POST'])
@faculty_decorator
def edit_profile():
    eForm = EditForm()
    if request.method == 'GET':
    #populate form data from the DB
        eForm.username.data = current_user.username
    elif request.method =='POST':
        if eForm.validate_on_submit():
            current_user.username = eForm.username.data
            current_user.set_password(eForm.password.data)

            db.session.add(current_user)
            db.session.commit()
            flash("Your changes have been made")
            return redirect(url_for('facultymain.display_profile'))
        else:
            print("Form not validated") #debugging purposes
    else:
        pass
    return render_template('faculty_edit_profile.html', title='Edit Profile', form = eForm)

@fmain.route('/faculty/postposition', methods=['GET', 'POST'])
@faculty_decorator
def postposition():
    pform = PostPositionForm()
    if pform.position_title.data and pform.validate_on_submit():
        new_position = ResearchPosition(
                        position_title = pform.position_title.data,
                        description = pform.description.data,
                        start_date = pform.start_date.data,
                        end_date = pform.end_date.data,
                        team_size = pform.team_size.data,
                        min_gpa = pform.min_gpa.data,
                        reference_required = pform.reference_required.data,
                        advisor_id = current_user.id)

        for major in pform.preferred_majors.data:
            new_position.preferred_majors.add(major)

        for topic in pform.research_topics.data:
            new_position.research_topics.add(topic)

        for lang in pform.required_languages.data:
            new_position.programming_languages.add(lang)

        for course in pform.required_courses.data:
            new_position.required_courses.add(course)

        db.session.add(new_position)
        db.session.commit()
        flash('Your position titled "' + new_position.position_title + '" has been created')
        return redirect(url_for('facultymain.mypositions'))
    return render_template('create_position.html', form = pform)

@fmain.route("/position/mypositions", methods = ['GET', 'POST'])
@faculty_decorator
def mypositions():
    emptyform = EmptyForm()
    new_ref = db.session.scalars(sqla.select(Application).where((Application.faculty_ref_id == current_user.id) & (Application.reference_status == Status.PENDING))).all()
    if (len(new_ref) != 0):
       flash("You have one or more pending reference requests. View your profile page for details.")
    return render_template('my_positions.html', title = 'My Positions', faculty = current_user, form=emptyform)

#ELLIOT TESTS
@fmain.route("/position/<position_id>/<application_id>", methods = ['GET'])
def view_app(position_id, application_id):
    if current_user.get_user_type() == "Student":
        flash("Faculty-only page. Student restricted.")
        return redirect(url_for('studentmain.index'))
    app = db.session.scalars(sqla.select(Application).where(Application.application_id == application_id)).first()
    pos = db.session.scalars(sqla.select(ResearchPosition).where(ResearchPosition.position_id == position_id)).first()
    if not app.position_id == pos.position_id:
        flash("Error occurred. Position ID {} is not equal to position ID stored in application ID {}.".format(pos.position_id, app.application_id))
    stud = db.session.scalars(sqla.select(Student).where(Student.id == app.applicant_id)).first()
    course_list = db.session.scalars(sqla.select(Course)).all()
    topic_list = db.session.scalars(sqla.select(ResearchTopic)).all()
    lang_list = db.session.scalars(sqla.select(ProgrammingLanguage)).all()
    major_list = db.session.scalars(sqla.select(Major)).all()

    lists: dict = {
        "courses": course_list,
        "topics": topic_list,
        "langs": lang_list,
        "majors": major_list
    }

    aform = ApproveForm()
    dform = DenyForm()

    return render_template('application_view.html', application = app, applicant = stud, position = pos, lists = lists, aform = aform, dform = dform)

@fmain.route("/position/<position_id>/<application_id>/approve", methods = ['POST'])
def approve_app(position_id, application_id):
    if current_user.get_user_type() == "Student":
        flash("Faculty-only page. Student restricted.")
        return redirect(url_for('studentmain.index'))
    app = db.session.scalars(sqla.select(Application).where(Application.application_id == application_id)).first()
    pos = db.session.scalars(sqla.select(ResearchPosition).where(ResearchPosition.position_id == position_id)).first()
    if not app.position_id == pos.position_id:
        flash("Error occurred. Position ID {} is not equal to position ID stored in application ID {}.".format(pos.position_id, app.application_id))
    stud = db.session.scalars(sqla.select(Student).where(Student.id == Application.applicant_id)).first()
    course_list = db.session.scalars(sqla.select(Course)).all()
    topic_list = db.session.scalars(sqla.select(ResearchTopic)).all()
    lang_list = db.session.scalars(sqla.select(ProgrammingLanguage)).all()
    major_list = db.session.scalars(sqla.select(Major)).all()

    lists: dict = {
        "courses": course_list,
        "topics": topic_list,
        "langs": lang_list,
        "majors": major_list
    }

    aform = ApproveForm()
    dform = DenyForm()
    if aform.validate_on_submit():
        if pos.get_number_accepted(application_id) == pos.team_size:
            flash("Cannot approve application: team size has been reached.")
        else:
            app.approve_application()
            db.session.add(app)
            db.session.commit()
            flash("Application approved.")
        return redirect(url_for('facultymain.mypositions'))

    return render_template('application_view.html', application = app, applicant = stud, position = pos, lists = lists, aform = aform, dform = dform)

@fmain.route("/position/<position_id>/<application_id>/deny", methods = ['POST'])
def deny_app(position_id, application_id):
    if current_user.get_user_type() == "Student":
        flash("Faculty-only page. Student restricted.")
        return redirect(url_for('studentmain.index'))
    app = db.session.scalars(sqla.select(Application).where(Application.application_id == application_id)).first()
    pos = db.session.scalars(sqla.select(ResearchPosition).where(ResearchPosition.position_id == position_id)).first()
    if not app.position_id == pos.position_id:
        flash("Error occurred. Position ID {} is not equal to position ID stored in application ID {}.".format(pos.position_id, app.application_id))
    stud = db.session.scalars(sqla.select(Student).where(Student.id == Application.applicant_id)).first()
    course_list = db.session.scalars(sqla.select(Course)).all()
    topic_list = db.session.scalars(sqla.select(ResearchTopic)).all()
    lang_list = db.session.scalars(sqla.select(ProgrammingLanguage)).all()
    major_list = db.session.scalars(sqla.select(Major)).all()

    lists: dict = {
        "courses": course_list,
        "topics": topic_list,
        "langs": lang_list,
        "majors": major_list
    }

    aform = ApproveForm()
    dform = DenyForm()
    if dform.validate_on_submit():
        app.reject_application()
        db.session.add(app)
        db.session.commit()
        flash("Application denied.")
        return redirect(url_for('facultymain.mypositions'))

    return render_template('application_view.html', application = app, applicant = stud, position = pos, lists = lists, aform = aform, dform = dform)

@fmain.route("/faculty/<student_id>/profile", methods = ['GET'])
@faculty_decorator
def view_student_profile(student_id):
    if (current_user.get_user_type() == "Faculty"):
        emptyform = EmptyForm()
        stud = db.session.scalars(sqla.select(Student).where(Student.id == student_id)).first()
        return render_template('display_profile.html', title = 'Display Profile', student = stud, form=emptyform)
    else:
        flash("Only Faculty can view other students profiles!")

@fmain.route("/positions/myposition/<position_id>", methods=['GET'])
@faculty_decorator
def my_position_details(position_id):
    position = db.session.get(ResearchPosition, position_id)
    if position is None:
        flash("Research position not found.")
        return redirect(url_for('facultymain.mypositions'))
    return render_template("my_position_details.html", title="Position Details", position=position)

@fmain.route("/positions/myposition/<position_id>/data", methods = ['GET'])
@faculty_decorator
def my_position_data(position_id):
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

@fmain.route("/positions/my/position/<position_id>/applications/data", methods=['GET'])
@faculty_decorator
def application_data(position_id):
    position = db.session.scalars(sqla.select(ResearchPosition).where(ResearchPosition.position_id == position_id)).first()
    position_apps = position.get_non_withdrawn_position_apps()
    applications: list = list()
    for app in position_apps:
        applications.append({
            "id": app.application_id,
            "applicant_name": app.applicant.get_fullname(),
            "status": app.application_status.value
        })

    data = {
        'position_title': position.position_title,
        'applications': applications # id, applicant_name, status
    }

    return jsonify(data)

@fmain.route("/faculty/requests", methods=['GET'])
@faculty_decorator
def view_requests():
    if current_user.get_user_type() == "Student":
        flash("Faculty-only page. Student restricted.")
        return redirect(url_for('studentmain.index'))
    references = current_user.get_ref_requests()
    aform = ApproveForm()
    dform = DenyForm()
    return render_template('view_requests.html', title = 'Reference Requests', references = references, aform = aform, dform = dform)

@fmain.route("/faculty/requests/<application_id>/accept", methods = ['POST'])
@faculty_decorator
def accept_request(application_id):
    app = db.session.scalars(sqla.select(Application).where(Application.application_id == application_id)).first()
    aform = ApproveForm()
    dform = DenyForm()
    if aform.validate_on_submit():
        app.approve_reference()
        db.session.add(app)
        db.session.commit()
        flash("Reference request approved.")
        return redirect(url_for('facultymain.display_profile'))
    references = current_user.get_ref_requests()
    return render_template('faculty_display_profile.html', references = references, aform = aform, dform = dform)

@fmain.route("/faculty/requests/<application_id>/deny", methods = ['POST'])
@faculty_decorator
def deny_request(application_id):
    app = db.session.scalars(sqla.select(Application).where(Application.application_id == application_id)).first()
    aform = ApproveForm()
    dform = DenyForm()
    if dform.validate_on_submit():
        app.reject_reference()
        db.session.add(app)
        db.session.commit()
        flash("Reference request rejected.")
        return redirect(url_for('facultymain.display_profile'))
    references = current_user.get_ref_requests()
    return render_template('faculty_display_profile.html', references = references, aform = aform, dform = dform)
