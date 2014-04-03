from flask import Blueprint, request, url_for, render_template, flash, g, session, redirect, url_for

from app import db
from app.questions.model import Question, Voter

import pprint as pp

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
                question.update({'last_vote': voter.last_vote(q)})

    return pp.pformat(question) # render_template('questions/vote.html', q)

@mod.route('/submit', methods=['POST'])
def submit():
    question_id = (int)(request.form['question_id'])
    vote_val = (int)(request.form['vote'])
    voter_id = request.cookies.get('voter_id')
    if voter_id is None or Voter.query.get(voter_id) is None:
        # create one!
        voter = Voter()
        db.session.add(voter)
        db.session.commit()
    else:
        voter = Voter.query.get(voter_id)
    voter.add_vote(Question.query.get(question_id), vote_val)

    return redirect(url_for(vote))

@mod.route('/show/<question_id>', methods=['GET'])
@mod.route('/show/<question_id>/', methods=['GET'])
def show(question_id):
    question = Question.query.get(int(question_id))
    if question is None:
        return 'Not found'
    # gather votes
    data = question.get_data()
    data.update({'votes': question.get_all_votes()})
    return str(data)


