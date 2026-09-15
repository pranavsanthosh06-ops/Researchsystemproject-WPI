from app import db, oauth
from flask import render_template, flash, redirect, url_for, session, request
import sqlalchemy as sqla
from app.models.models import Student, User
from .studauth_forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from . import studentauth_blueprint as sauth
from authlib.integrations.flask_client import OAuth
from os import environ as env
from urllib.parse import urlencode, quote_plus

@sauth.route('/student/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('studentmain.index'))
    rform = RegistrationForm()
    if rform.validate_on_submit():
        user = Student(username = rform.username.data,
                       firstname = rform.firstname.data,
                       lastname = rform.lastname.data,
                       email = rform.email.data,
                       wpi_id = rform.wpi_id.data,
                       gpa = rform.gpa.data)
        user.set_password(rform.password.data)
        for m in rform.majors.data:
            user.majors_of_student.add(m)

        for topic in rform.research_topics.data:
            user.topics_of_interest.add(topic)

        for lang in rform.programming_languages.data:
            user.languages_known.add(lang)

        db.session.add(user)
        db.session.commit()
        flash("You are now a registered user.")
        return redirect(url_for('studentauth.login'))
    return render_template('register.html', form = rform)

@sauth.route('/student/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('studentmain.index'))
    lform = LoginForm()
    if lform.validate_on_submit():
        query = sqla.Select(User).where(User.username == lform.username.data)
        user = db.session.scalars(query).first()
        if (user is None) or (user.check_password(lform.password.data) == False):
            flash('Unsuccessful login attempt')
            return redirect(url_for('studentauth.login'))
        else:
            login_user(user, remember= lform.remember_me.data)
            if current_user.get_user_type() == "Student":
                flash('The student {} has successfully logged in!'.format(current_user.username))
                return redirect(url_for('studentmain.index'))
            elif current_user.get_user_type() == "Faculty":
                flash('The faculty member {} has successfully logged in!'.format(current_user.username))
                return redirect(url_for('facultymain.mypositions')) # set to facultymain after creation
            else:
                flash('fatal error has occurred')
    return render_template('login.html', form=lform)

@sauth.route("/student/logout", methods = ['GET'])
@login_required
def logout():
    if current_user.get_user_type() == "Faculty":
        return redirect(url_for('facultyauth.logout'))
    logout_user()
    return redirect(url_for('studentauth.login'))

@sauth.route("/ssologin", methods = ['GET'])
def ssologin():
    return oauth.auth0.authorize_redirect(
        redirect_uri = url_for("studentauth.callback", _external = True)
    )

@sauth.route("/callback", methods = ['GET'])
def callback():
    error = request.args.get("error")
    if error:
        flash("SSO Login Failed: " + error)
        return redirect("/welcome")
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    user_email = token["userinfo"]["email"]
    user = db.session.scalars(sqla.select(User).where(User.email == user_email)).first()

    if user is None or (user.get_user_type() == 'Faculty' and user.activated == False):
        flash("Please register or activate your account before signing in via SSO.")
        return redirect("/welcome")
    else:
        login_user(user)
        if user.get_user_type() == 'Student':
            return redirect(url_for("studentmain.index"))
        else:
            return redirect(url_for("facultymain.mypositions"))

#token = oauth.auth0.authorize_access_token()
#session["user"] = token

#should be called only after logout_user()
# should add login route url to Allowed Logout URLs in Auth0 settings    
@sauth.route("/ssologout", methods = ['GET'])
def ssologout():
    logout_user()
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN") + "/v2/logout?"+ 
        urlencode(
            {
                "returnTo": url_for("studentauth.login", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )