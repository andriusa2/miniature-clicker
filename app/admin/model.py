
from app import db


class User(db.Model):

    # PK
    id = db.Column(db.Integer, primary_key=True)

    # Data
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    # relations
    raised_questions = db.relationship('Question', backref='user', lazy='dynamic')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password  # might want to hash this, rite

    def __repr__(self):
        return '<User %r>' % self.username

    def get_all_questions(self):
        return self.questions.all()

    def get_all_votes(self):
        return self.votes.all()
