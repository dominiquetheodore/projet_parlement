
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import PQ, Base, Deputy, Session
import re
from os import remove, listdir
from os.path import isfile, join, exists
from datetime import datetime, timedelta

engine = create_engine('sqlite:///PQs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

deputies = session.query(Deputy).all()
for deputy in deputies:
	deputy.count = deputy.count_pqs(deputy)
	print deputy.count
	session.add(deputy)

sessions = session.query(Session).all()
for sess in sessions:
	sess.count = sess.count_pqs(sess)
	print sess.count
	session.add(sess)

session.commit()
