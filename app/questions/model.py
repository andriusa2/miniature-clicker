"""
DB model for questions part of the project

Includes
"""

from app import db
import pickle
from datetime import datetime


class Question(db.Model):
    # PK
    id = db.Column(db.Integer, primary_key=True)

    # FK
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # payload
    question_data = db.Column(db.PickleType)
    started = db.Column(db.DateTime)
    finishes = db.Column(db.DateTime)

    # relations
    # all votes cast to this one - 1 -> many
    votes = db.relationship('Vote', backref='question', lazy='dynamic')

    @staticmethod
    def get_ongoing():
        now = datetime.now()
        return Question.query.filter(Question.finishes > now).filter(Question.started <= now).first()

    @staticmethod
    def get_all(not_started_only=False):
        if not_started_only:
            now = datetime.now()
            return Question.query.filter(Question.started <= now).all()
        return Question.query.all()

    def get_data(self):
        data = pickle.loads(self.question_data)
        data.update({'started': self.started, 'finishes': self.finishes}.items())
        return data

    def get_all_votes(self):
        return self.votes.all()


class Vote(db.Model):

    # FK
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)

    # payload
    vote_val = db.Column(db.Integer)
    time = db.Column(db.DateTime)


class Voter(db.Model):
    # PK
    id = db.Column(db.Integer, primary_key=True)

    # relations
    votes = db.relationship('Vote', backref='voter', lazy='dynamic')

