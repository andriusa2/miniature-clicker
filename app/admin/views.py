from flask import Blueprint, request, url_for, make_response, render_template, flash, g, session, redirect
from flask.ext.login import LoginManager, login_user, login_required, logout_user

from app.admin.forms import LoginForm, RegistrationForm


from app import db, login_manager
from app.questions.model import Question, User


mod = Blueprint('admin', __name__)


@login_manager.user_loader
def load_user(userid):
    print(userid)
    return User.query.get(int(userid))

@mod.route("/add_user/", methods=["GET", "POST"])
@login_required
def add_user():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash('Successfully registered %s' % form.username.data)
        return redirect(url_for('.add_user', methods=['GET']))
    return render_template('admin/register.html', form=form)


@mod.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Successfully logged in as %s" % form.user.username)
        login_user(form.user)
        return redirect(request.args.get("next") or url_for(".show_all"))
    return render_template('admin/login.html', form=form) # render_template("admin/login.html", form=form)


@mod.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))

@mod.route("/admin/show/all/")
@login_required
def show_all():
    questions = Question.get_all(not_started_only=False)
    if questions is None:
        return 'No questions found'
    data = list(map(lambda a: a.get_data(), questions))
    return str(data)

@mod.route("/admin/edit/<qid>", methods=['GET'])
@login_required
def show_edit(qid):
    data = Question.query.get(qid)
    if data is None:
        flash('No such question exists')
        return redirect(url_for('.show_all'))
    data = data.get_data()
    return str(data)


@mod.route("/admin/test_edit/<qid>/<field>/<val>", methods=['GET'])
def test_submit_edit(qid, field, val):
    data = Question.query.get(qid)

    if data is None:
        flash('No such question exists')
        return redirect(url_for('.show_all'))
    data.update_field(field, val)
    return str(data.get_data())

@mod.route("/admin/edit/<qid>", methods=['POST'])
@login_required
def submit_edit(qid):
    data = Question.query.get(qid)
    if data is None:
        flash('No such question exists')
        return "No question found", 500
    field, val = request.form['field'], request.form['val']
    data.update_field(field, val)
    return "Set successfully"
    # TODO: copy over data, commit db

@mod.route("/admin/show/<qid>", methods=['POST'])
def show_question(qid):
    raise NotImplementedError
    # TODO: show time controls, etc
