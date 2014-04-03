from app import db

# generate some fresh data

# add dummy data
from app.admin.model import User as U
from app.questions.model import Question as Q, Vote as V

db.drop_all()
db.create_all()
import pickle

db.session.add(U(username='abc', password='pwd', email='lol@lol'))
dummy_question = {
    'title': 'Lolcats',
    'options': [
        'abc', 'def', 'ghi'
    ]
}
db.session.commit()

uid = U.query.first().id
import datetime
db.session.add(Q(owner_id=uid, question_data=pickle.dumps(dummy_question),
                 started=datetime.datetime(1,2,3), finishes=datetime.datetime(1,2,3)))
db.session.commit()
qid = Q.query.first().id
db.session.add(V(voter_id=uid, question_id=qid, vote_val=1, time=datetime.datetime(1,2,3)))
db.session.commit()
print(Q.query.first().get_data())