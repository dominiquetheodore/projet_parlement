
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, PQ, Deputy, Session, Constituency, User, Party, PNQ
import re
from os import remove, listdir
from os.path import isfile, join, exists
from datetime import datetime, timedelta
import io, json

engine = create_engine('sqlite:///PQs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

parties = session.query(Party.name).all()
labels = [ ]
by_party = dict()
latest_sessions = session.query(Session.id, Session.date).order_by(Session.date.desc()).limit(20)

deps = session.query(Deputy.id).all()

for sess in latest_sessions:
    dat = sess.date.strftime('%b-%d-%Y')
    by_party[dat] = {}
    for party in parties:
        by_party[dat][party.name] = 0
    labels.append(dat)

    pqs = session.query(PQ.deputy_id).filter_by(session_id=sess.id).all()
    for pq in pqs:
        party_id = session.query(Deputy.party_id).filter_by(id=pq.deputy_id).one()
        part = session.query(Party.name).filter_by(id=party_id[0]).one()
        by_party[dat][part.name] += 1

values_MMM = []
values_MSM = []
values_ML = []
values_PTr = []
values_PMSD = []
values_MP = []

values = dict()

for sess, item in by_party.items():
	for party in parties:
		values[party.name] = []

for sess, item in by_party.items():
	for party in parties:
		values[party.name].append(item[party.name])
	
with io.open('graph.json', 'w', encoding='utf-8') as f:
  f.write(unicode(json.dumps(values, ensure_ascii=False)))

print 'done'
