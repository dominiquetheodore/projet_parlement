import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import PQ, Deputy, Base, Constituency
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

with open('csv/constituencies.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',')
	rows = list(spamreader)
	for row in rows[1:]:
		constituency = Constituency(id=unicode(row[0], "utf-8"), constituency=unicode(row[1], "utf-8"))
		session.add(constituency)
		session.commit()

