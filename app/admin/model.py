
from app import db, bcrypt

class User(db.Model):

    # PK
    id = db.Column(db.Integer, primary_key=True)

    # Data
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))

    # relations
    raised_questions = db.relationship('Question', backref='owner', lazy='dynamic')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = User.hash_pwd(password)

    def __repr__(self):
        return '<User %r>' % self.username

    def get_all_questions(self):
        return self.questions.all()

    def get_all_votes(self):
        return self.votes.all()

    def check_password(self, pwd):
        return bcrypt.check_password_hash(self.password, pwd)

    @staticmethod
    def hash_pwd(pwd):
        return bcrypt.generate_password_hash(pwd)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)