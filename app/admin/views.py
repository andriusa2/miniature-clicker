from flask import Blueprint, request, url_for, make_response, render_template, flash, g, session, redirect, json
from flask.ext.login import login_user, login_required, logout_user, current_user
import datetime
from app.admin.forms import LoginForm, RegistrationForm


from app import db, login_manager
from app.questions.model import Question, User


mod = Blueprint('admin', __name__)


@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@mod.route("/admin/add_user/", methods=["GET", "POST"])
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
    return render_template('admin/login.html', form=form, logged_in=current_user.is_authenticated())


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

@mod.route("/admin/add_question/", methods=['GET', 'POST'])
@mod.route("/admin/edit/", methods=['GET', 'POST'])
@mod.route("/admin/edit/<qid>/", methods=['GET', 'POST'])
@login_required
def edit(qid=None):
    if request.method == 'POST':
        req_fields = Question.get_fields()
        if req_fields - set(request.form.keys()) != set([]):
            flash('Not enough data')
            return redirect(url_for('.edit', qid=None))

        data = None
        if qid is not None:
            data = Question.query.get(int(qid))
            if data is not None:
                # update question
                if data.started:
                    started = data.started
                    finishes = started + datetime.timedelta(seconds=int(request.form['duration']))
                else:
                    finishes = datetime.datetime.min + datetime.timedelta(seconds=int(request.form['duration']))
                    started = None
                options = request.form.getlist('options')
                while options and not options[-1]:
                    options.pop()
                if not options or '' in options:
                    flash('Inconsistent option edit')
                    return redirect(url_for('.edit', qid=qid))
                data.finishes = finishes
                data.started = started
                data.update_field('options', options, delayed_commit=True)
                data.update_field('correct', int(request.form['correct']), delayed_commit=True)
                data.update_field('title', request.form['title'], delayed_commit=True)
                data.update_field('description', request.form['description'], delayed_commit=True)
                db.session.commit()
                return redirect(url_for('.edit', qid=qid))
    # add new question

    # full update
        finishes = datetime.datetime.min + datetime.timedelta(seconds=int(request.form['duration']))
        started = None
        options = request.form.getlist('options')

        while options and not options[-1]:
            options.pop()
        if not options or '' in options:
            flash('Inconsistent option edit')
            return redirect(url_for('.edit', qid=qid))
        question = Question(owner=current_user, finishes=finishes, options=options,
                            started=started, title=request.form['title'], description=request.form['description'], correct=int(request.form['correct']))

        db.session.add(question)
        db.session.commit()
        flash('Question added successfully')
        return redirect(url_for('.show_all'))
    data = None
    if qid is not None:
        data = Question.query.get(int(qid))
        if data:
            data = data.get_data()
    return render_template('admin/edit.html', question=data)



@mod.route("/admin/show/<qid>/", methods=['POST'])
def show_question(qid):
    raise NotImplementedError
    # TODO: show time controls, etc

@mod.route("/admin/start/<qid>/", methods=['GET', 'POST'])
@login_required
def start_question(qid):
    if Question.get_ongoing():
        flash("There is ongoing vote, you can't start another one now")
        return redirect(url_for('.show_all'))
    q = Question.query.get(qid)
    if not q:
        flash("No such id")
        return redirect(url_for('.show_all'))
    q.start()
    return redirect(url_for('questions.vote'))

@mod.route("/admin/pause/<qid>/", methods=['GET', 'POST'])
@login_required
def pause_question(qid):
    q = Question.query.get(qid)
    if not q:
        flash("No such id")
        return redirect(url_for('.show_all'))
    q.pause()
    return redirect(url_for('questions.show',question_id=qid))

@mod.route("/admin/stop/<qid>/", methods=['GET', 'POST'])
@login_required
def stop_question(qid):
    q = Question.query.get(qid)
    if not q:
        flash("No such id")
        return redirect(url_for('.show_all'))
    q.stop()
    return redirect(url_for('questions.show', question_id=qid))

@mod.route("/admin/votes/<qid>/count/", methods=['GET', 'POST'])
@login_required
def get_vote_count(qid):
    q = Question.query.get(qid)
    if not q:
        flash("No such id")
        return redirect(url_for('.show_all'))
    return json.dumps({'d': q.get_vote_count(), 'completed': q.completed()})