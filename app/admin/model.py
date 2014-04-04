
from app import db
import bcrypt
# from flaskext.bcrypt import generate_password_hash, check_password_hash

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
    # fix this
    def check_password(self, pwd):
        print(self.password)
        cand = bcrypt.hashpw(pwd, self.password)
        print(cand)
        return self.password == cand

    @staticmethod
    def hash_pwd(pwd):
        # if isinstance(pwd, unicode):
        #     pwd = pwd.encode('u8')
        # pwd = str(pwd)
        return bcrypt.hashpw(pwd, bcrypt.gensalt(12))

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)