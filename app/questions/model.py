"""
DB model for questions part of the project

Includes
"""

from app import db
import pickle
# from app.admin.model import User


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

    def get_all_votes(self):
        return list(self.votes)

    @staticmethod
    def get_ongoing():
        return Question.query.first()

    def get_data(self):
        return pickle.loads(self.question_data)


class Vote(db.Model):
    # __table_args__ = (
    #     UniqueConstraint("id", "candidate_id"),
    # )
    # PK
    #id = db.Column(db.Integer, primary_key=True)

    # FK
    voter_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)

    # payload
    vote_val = db.Column(db.Integer)
    time = db.Column(db.DateTime)
