from app import db

# generate some fresh data

# add dummy data
from app.admin.model import User as U
from app.questions.model import Question as Q, Vote as V, Voter as Vr

import datetime
import pickle
from random import randint
# reset database
db.drop_all()
db.create_all()

def get_random_date(date):
    return date + datetime.timedelta(days=-randint(1,10))

def get_dummy_question_options(i):
    return {
        'title': 'Question %d' % i,
        'options': ['Option %d' % j for j in range(4)],
        'correct': i % 4
    }
def create_users(n=5):
    us = []
    for i in range(n):
        us.append(U(username='User%d' % i, password='pwd', email='abc%d' % i))
        db.session.add(us[-1])
    db.session.commit()
    return us

# n => how many in total
# l => how many
def create_questions(us, n=5, l=2):
    qs = []
    minute = datetime.timedelta(minutes=1)
    day = datetime.timedelta(days=1)
    u = us[0]
    now = datetime.datetime.now()
    for i in range(l):
        st = get_random_date(now)
        qs.append(Q(owner=u, started=st, finishes=st+minute, **get_dummy_question_options(i)))
        db.session.add(qs[-1])
    for i in range(n-1):
        st = get_random_date(now)
        qs.append(Q(owner=us[(i+1)%len(us)], started=st, finishes=st+minute, **get_dummy_question_options(i)))
        db.session.add(qs[-1])
    qs.append(Q(owner=u, started=now, finishes=now+day, **get_dummy_question_options(1)))
    db.session.add(qs[-1])
    db.session.commit()
    return qs

# n = how many votes for each question
# l = how many votes for first question
def create_votes(qs, n=2, l=5):
    vs = []
    # first of all create voters
    voters = []
    for i in range(max(len(qs), l, n) + 1):
        voters.append(Vr())
        db.session.add(voters[-1])
    db.session.commit()
    second = datetime.timedelta(seconds=1)
    for i in range(l):
        vs.append(V(voter=voters[i], question=qs[0], vote_val=randint(0,3), time=qs[0].started+(i+1)*second))
        db.session.add(vs[-1])
    v = 0
    for q in qs[1:]:
        for i in range(n):
            vs.append(V(voter=voters[v], question=q, vote_val=randint(0,3), time=q.started+(i+1)*second))
            db.session.add(vs[-1])
            v+=1
            v%=len(voters)
    db.session.commit()
    return voters, vs


def default_battery():
    us = create_users(3)
    qs = create_questions(us)
    voters, vs = create_votes(qs)