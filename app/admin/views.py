from flask import Blueprint, request, url_for, make_response, render_template, flash, g, session, redirect
from flask.ext.login import login_user, login_required, logout_user, current_user
import datetime
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
    return render_template('admin/register.html', form=form, logged_in=current_user.is_authenticated())


@mod.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Successfully logged in as %s" % form.user.username)
        login_user(form.user)
        return redirect(request.args.get("next") or url_for(".show_all"))
    return render_template('admin/login.html', form=form, logged_in=current_user.is_authenticated()) # render_template("admin/login.html", form=form)


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
    return render_template("questions/all_q.html",questions=data, logged_in=current_user.is_authenticated())

@mod.route("/admin/edit/<qid>/", methods=['GET'])
@login_required
def edit(qid):
    data = Question.query.get(qid)
    if data is None:
        flash('Error: question not found')
        return redirect(url_for('.show_all'))
    data = data.get_data()
    return render_template("admin/edit.html", question=data, logged_in=current_user.is_authenticated())


@mod.route("/admin/test_edit/<qid>/<field>/<val>/", methods=['GET'])
def test_submit_edit(qid, field, val):
    """
    Field should be in . notation, e.g. data[a][b] => a.b
    """
    data = Question.query.get(qid)

    if data is None:
        flash('Error: question not found')
        return redirect(url_for('.show_all'))
    data.update_field(field, val)
    return str(data.get_data())

@mod.route("/admin/edit/<qid>/", methods=['POST'])
@login_required
def submit_edit(qid):
    data = Question.query.get(qid)
    if data is None:
        flash('Error: question not found')
        return "No question found", 500
    # full update
    finishes = datetime.datetime.min + datetime.timedelta(seconds=int(request.form['duration']))
    started = None
    options = request.form.getlist('options')
    data.finishes = finishes
    data.started = started
    data.update_field('options', options, delayed_commit=True)
    data.update_field('correct', request.form['correct'], delayed_commit=True)
    data.update_field('title', request.form['title'], delayed_commit=True)
    data.update_field('description', request.form['description'], delayed_commit=True)
    db.session.commit()
    return "Set successfully"


@mod.route("/admin/add_question/", methods=['GET', 'POST'])
@login_required
def add_question():
    if request.method == 'POST':
        print(request.form)
        req_fields = Question.get_fields()
        if req_fields - set(request.form.keys()) == set([]):
            finishes = datetime.datetime.min + datetime.timedelta(seconds=int(request.form['duration']))
            started = None
            options = request.form.getlist('options') # [val for q, val in request.form.items() if q == 'options']
            question = Question(owner=current_user, finishes=finishes, options=options,
                                started=started, title=request.form['title'], description=request.form['description'], correct=request.form['correct'])

            db.session.add(question)
            db.session.commit()
            flash('Question added successfully')
            return redirect(url_for('.show_all'))
        flash('Not enough data provided')
    return render_template('admin/add_question.html', logged_in=current_user.is_authenticated())



@mod.route("/admin/show/<qid>", methods=['POST'])
def show_question(qid):
    raise NotImplementedError
    # TODO: show time controls, etc
