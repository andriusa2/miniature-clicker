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


def to_js_timestamp(time):
    epoch = datetime.utcfromtimestamp(3*60*60)  # TODO - fix for timezones
    delta = time - epoch
    return delta.total_seconds() * 1000.0

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
    _data = None
    # relations
    # all votes cast to this one - 1 -> many
    votes = db.relationship('Vote', backref='question', lazy='dynamic')

    def __init__(self, title, options, correct, owner, started, finishes, *args, **kwargs):
        self.question_data = pickle.dumps({
            'title': title,
            'options': options,
            'correct': int(correct)
        })
        self.owner = owner
        self.started = started
        self.finishes = finishes

    @staticmethod
    def get_fields():
        return {
            'title', 'options', 'correct', 'duration', 'description'
        }
    @staticmethod
    def get_ongoing():
        now = datetime.now()
        return Question.query.filter(Question.finishes > now).filter(Question.started <= now).first()

    @staticmethod
    def get_all(not_started_only=False):
        if not_started_only:
            now = datetime.now()
            return Question.query.filter(Question.started <= now).order_by(Question.finishes.desc()).all()
        questions = list(Question.query.order_by(Question.finishes.desc()).all())
        # now take all those which aren't started and put them to the start of the list
        live, waiting = [], []

        for item in questions:
            (live if item.started is not None else waiting).append(item)
        return waiting + live

    def _load_data(self):
        if not self._data:
            self._data = pickle.loads(self.question_data)

    def _prep_data(self):
        self._load_data()
        self.data = {
            'id': self.id,
            'started': self.started,
            'finishes': self.finishes,
            'finishes_js': to_js_timestamp(self.finishes),
            'vote_distr': self.get_vote_distribution(),
            'completed': self.completed(),
            'ongoing': self.ongoing(),
            'duration': self.duration(),
        }

    def duration(self):
        if self.started is None:
            return int((self.finishes - datetime.min).total_seconds())
        else:
            return int((self.finishes - self.started).total_seconds())

    def completed(self):
        now = datetime.now()
        return now > self.finishes and self.started is not None

    def ongoing(self):
        now = datetime.now()
        return self.started is not None and self.started <= now < self.finishes

    def get_data(self):
        if not self.data:
            self._prep_data()
        return dict(list(self.data.items()) + list(self._data.items()))

    def get_all_votes(self):
        return self.votes.all()

    def get_vote_count(self):
        return self.votes.count()

    def valid_value(self, val):
        if not self.data:
            self._prep_data()
        return 0 <= val < len(self._data['options'])

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
            'total': sum_votes,
            'distr': list(votes),
            'vote_split':
            [{
                'percentage': float(v)/float(sum_votes),
                'votes': v,
                'option': opt
                } for opt, v in distr.items()
            ]
        }
        return retval

    def update_field(self, field, val, delayed_commit=False):
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
        self.question_data = pickle.dumps(self._data)
        if not delayed_commit:
            db.session.commit()

    def add_option(self, value=None):
        if not value:
            value = "Option"
        self._load_data()
        self._data['options'].append(value)
        self._update_data()

    @staticmethod
    def get_empty_data():
        return {
            'title': 'Dummy name',
            'options': [],
            'correct': None
        }

    def start(self):
        if not self.ongoing():
            if self.started is None:
                self.started = datetime.now()
                self.finishes += self.started - datetime.min
                db.session.commit()

    def stop(self):
        if self.ongoing():
            self.finishes = datetime.now()
            db.session.commit()

    def pause(self):
        if self.ongoing():
            self.finishes = self.finishes - datetime.now() + datetime.min
            self.started = None
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
