from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

from app import db
from app.questions.model import Question, Vote

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
    return pp.pformat(question) # render_template('questions/vote.html', q)
