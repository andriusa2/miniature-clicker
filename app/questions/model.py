"""
DB model for questions part of the project

Includes
"""

from app import db
import pickle
from collections import defaultdict
from datetime import datetime
from app.admin.model import User
from sqlalchemy import func


class Question(db.Model):
    # PK
    id = db.Column(db.Integer, primary_key=True)

    # FK
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # payload
    question_data = db.Column(db.PickleType)
    started = db.Column(db.DateTime)
    finishes = db.Column(db.DateTime)

    data = None
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

    def _prep_data(self):
        self._data = pickle.loads(self.question_data)
        self.data = {
            'id': self.id,
            'started': self.started,
            'finishes': self.finishes,
            'vote_distr': self.get_vote_distribution()
        }

    def get_data(self):
        if not self.data:
            self._prep_data()
        return dict(list(self.data.items()) + list(self._data.items()))

    def get_all_votes(self):
        return self.votes.all()

    def valid_value(self, val):
        if not self.data:
            self._prep_data()
        return 0 <= val < len(self.data['options'])

    def alter_finish(self, td):
        self.finishes += td
        db.session.commit()

    def get_vote_distribution(self):
        votes = self.get_all_votes()
        distr = defaultdict(lambda: 0)
        for vote in votes:
            distr[vote.vote_val] += 1

        sum_votes = sum(distr.values())

        retval = {
            opt: {
                'percentage': float(v)/float(sum_votes),
                'votes': v
            } for opt, v in distr.items()
        }
        retval.update({
            'total': sum_votes,
            'distr': list(votes)
        })
        return retval

    def update_field(self, field, val):
        # TODO: validate if that's viable update
        self.get_data()
        fields = field.split('.')
        fs = []
        for f in fields:
            try:
                fs.append(int(f))
            except:
                fs.append(f)
        root = self._data
        for f in fs[:-1]:
            try:
                root = root[f]
            except:
                print(root.keys())
                print("Field %s not found[%s]" % (field, f))
                return
        root[fs[-1]] = val
        self.question_data = pickle.dumps(self.data)
        db.session.commit()


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

    def get_votes(self):
        return self.votes.all()

    def has_voted(self, question):
        return self.last_vote(question) is not None

    def last_vote(self, question):
        return self.votes.filter(Vote.question == question).first()

    @staticmethod
    def can_vote(question, value=None):
        now = datetime.now()
        if question.started <= now < question.finishes:
            if value is None:
                return True
            if question.valid_value(value):
                return True
        return False

    def add_vote(self, question, value):
        if question is None:
            raise ValueError("No question?")
        if self.can_vote(question, value):
            if self.has_voted(question):
                v = self.last_vote(question)
                v.vote_val = value
                v.time = datetime.now()
            else:
                vote = Vote(question=question, vote_val=value, time=datetime.now(), voter=self)
                db.session.add(vote)
            db.session.commit()
        else:
            raise ValueError("User can't vote on this question")
