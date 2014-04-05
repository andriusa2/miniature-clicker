
from flask_wtf import Form
from wtforms import TextField, PasswordField, validators, IntegerField, TextAreaField

from app.admin.model import User


class LoginForm(Form):
    username = TextField('Username', [validators.Required(),])
    password = PasswordField('Password', [validators.Required(),])

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False  # should be enabled!
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        # rv = Form.validate(self)
        # if not rv:
        #     return False

        user = User.query.filter_by(username=self.username.data).first()
        if user is None:
            print('user not found')
            self.username.errors = []
            self.username.errors.append('Unknown username')
            return False

        if not user.check_password(self.password.data):
            self.password.errors = []
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True


class RegistrationForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    email = TextField('Email Address', [validators.Required()])

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False  # should be enabled!
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = super(RegistrationForm, self).validate()
        if not rv:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            self.username.errors = []
            self.username.errors.append('User with this username already exists')
            return False

        return True
