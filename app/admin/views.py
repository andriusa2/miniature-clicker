from flask import Blueprint, request, url_for, make_response, render_template, flash, g, session, redirect
from flask.ext.login import LoginManager, login_user, login_required, logout_user
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired


from app import db
from app.questions.model import Question, User


class LoginForm(Form):
    username = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user is None:
            self.username.errors.append('Unknown username')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True

mod = Blueprint('admin', __name__)

login_manager = LoginManager()


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


@mod.route("/add_user/", methods=["GET"])
def add_user():
    return "A form for adding an user"

@mod.route("/add_user/", methods=["POST"])
def add_user_submit():
    username = request.form['username']
    password = request.form['password']
    #password =
    email = request.form['email']
    user = User(username=username, password=password, email=email)


@mod.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Successfully logged in as %s" % form.user.username)
        login_user(form.user)
        return redirect(request.args.get("next") or url_for("index"))
    return ''.join(['<form action="login" method="post">Username: ', str(form.username), '<br/>Password: ', str(form.password),
                    '<br/><input type="submit"></form>']) # render_template("admin/login.html", form=form)


@mod.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))

@mod.route("/admin/show/all")
@login_required
def show_all():
    questions = Question.get_all(not_started_only=False)
    if questions is None:
        return 'No questions found'
    data = map(lambda a: a.get_data(), questions)
    return str(data)

@mod.route("/admin/edit/<qid>", methods=['GET'])
def show_edit(qid):
    data = Question.query.get(qid)
    if data is None:
        flash('No such question exists')
        return redirect(url_for('.show_all'))
    data = data.get_data()
    return str(data)

@mod.route("/admin/edit/<qid>", methods=['POST'])
def submit_edit(qid):
    data = Question.query.get(qid)
    if data is None:
        flash('No such question exists')
        return redirect(url_for('.show_all'))
    raise NotImplementedError
    # TODO: copy over data, commit db

@mod.route("/admin/show/<qid>", methods=['POST'])
def show_question(qid):
    raise NotImplementedError
    # TODO: show time controls, etc
