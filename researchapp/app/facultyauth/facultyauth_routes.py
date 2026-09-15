from app import db, mail
from flask import render_template, flash, redirect, url_for, session
import sqlalchemy as sqla
from app.models.models import User
from app.facultyauth.facultyauth_forms import ActivationForm, VerifyForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from app.facultyauth import facultyauth_blueprint as fauth
from flask_mail import Message
from random import randint

def send_email(recipient: str) -> str:
    """
    Creates and sends a verification email to given recipient.

    Parameters:
        recipient (str): email of the recipient

    Returns:
        str: verification code sent to the recipient
    """
    code: str = str(randint(10000000, 99999999))
    body_string: str = "Thank you for registering for ResearchConnect! Please enter the following code to verify your account: {}.".format(code)
    msg = Message(
        subject='ResearchConnect Verification',
        recipients=[recipient],
        body=body_string
    )

    mail.send(msg)

    return code

@fauth.route('/faculty/activate', methods = ['GET', 'POST'])
def activate():
    if current_user.is_authenticated:
        return redirect(url_for('facultymain.mypositions'))
    aform = ActivationForm()
    vform = VerifyForm()
    session['verification_code'] = ""
    return render_template('activate.html', aform = aform, vform = vform)

@fauth.route('/faculty/activate/verify', methods=['POST'])
def verify():
    if current_user.is_authenticated:
        return redirect(url_for('facultymain.mypositions'))
    aform = ActivationForm()
    vform = VerifyForm()
    if aform.submit.data and aform.validate():
        faculty = aform.email.data
        code = send_email(faculty.email)
        session['faculty_email'] = faculty.email
        session['verification_code'] = code
        flash("Please check your email")
    return render_template('activate.html', aform = aform, vform = vform)

@fauth.route('/faculty/activate/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('facultymain.mypositions'))
    aform = ActivationForm()
    vform = VerifyForm()
    if vform.submit.data and vform.validate():
        code = session.get('verification_code')
        if code == "":
            flash("No email selected. Please try again.")
            return redirect(url_for('facultyauth.activate'))

        faculty_email = session.get('faculty_email')
        faculty = db.session.scalars(sqla.select(User).where(User.email == faculty_email)).first()

        if code == vform.code.data:
            faculty.username = vform.username.data
            faculty.set_password(vform.password.data)
            faculty.activated = True
            db.session.add(faculty)
            db.session.commit()
            flash("User validated")
            return redirect(url_for('studentmain.index'))
        else:
            flash("Validation failed. Please try again.")
    return render_template('activate.html', aform = aform, vform = vform)

@fauth.route('/faculty/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('facultymain.mypositions'))
    lform = LoginForm()
    if lform.validate_on_submit():
        user = db.session.scalars(sqla.select(User).where(User.username == lform.username.data)).first()
        if (user is None) or (user.check_password(lform.password.data) == False):
            flash('Invalid username or password!')
            return redirect(url_for('facultyauth.login'))
        else:
            login_user(user, remember=lform.remember_me.data)
            if current_user.get_user_type() == "Student":
                flash('The student {} has successfully logged in!'.format(current_user.username))
                return redirect(url_for('studentmain.index'))
            elif current_user.get_user_type() == "Faculty":
                flash('The faculty member {} has successfully logged in!'.format(current_user.username))
                return redirect(url_for('facultymain.mypositions'))
            else:
                flash('fatal error has occurred')
    return render_template('login.html', form = lform)

@fauth.route("/faculty/logout", methods = ['GET'])
@login_required
def logout():
    if current_user.get_user_type() == "Student":
        return redirect(url_for('studentmain.logout'))
    logout_user()
    return redirect(url_for('facultyauth.login'))
