from flask import Blueprint, request, url_for, make_response, render_template, flash, g, session, redirect

from app import db
from app.questions.model import Question, Voter

mod = Blueprint('questions', __name__)


@mod.route('/')
def vote():
    # get the current ongoing quiz
    q = Question.get_ongoing()
    if q is None:
        return 'Nothing, lol' # render_template('questions/nothing.html')

    # unpickle the data structure then
    question = q.get_data()
    voter_id = request.cookies.get('voter_id')
    if voter_id is not None:
        # maybe you have already voted?
        voter = Voter.query.get(int(voter_id))
        if voter:
            if voter.has_voted(q):
                question.update({'last_vote_val': voter.last_vote(q).vote_val})

    return render_template('questions/voting.html', question=question)


@mod.route('/submit/', methods=['POST'])
def submit():
    question_id = int(request.form['question_id'])
    vote_val = int(request.form['vote'])
    voter_id = request.cookies.get('voter_id')
    set_cookie = False
    if voter_id is None or Voter.query.get(voter_id) is None:
        # create one!
        voter = Voter()
        db.session.add(voter)
        db.session.commit()
        set_cookie = True
    else:
        voter = Voter.query.get(voter_id)
    try:
        voter.add_vote(Question.query.get(question_id), vote_val)
    except Exception as e:
        print(e)
        flash("Your vote couldn't be registered")
    else:
        flash("You have successfully voted")

    if set_cookie:
        resp = make_response(redirect(url_for('.vote')))
        resp.set_cookie('voter_id', str(voter.id))
        return resp
    return redirect(url_for('.vote'))


@mod.route('/show/<question_id>/', methods=['GET'])
def show(question_id):
    question = Question.query.get(int(question_id))
    if question is None:
        return 'Not found'
    # gather votes
    data = question.get_data()
    return render_template('questions/results.html', question=data)


@mod.route('/show/all/', methods=['GET'])
def show_all():
    questions = Question.get_all(not_started_only=True)
    if questions is None:
        return 'No questions found'
    data = list(map(lambda a: a.get_data(), questions))
    return str(data)
