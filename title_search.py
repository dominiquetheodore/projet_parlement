
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import PQ, Base
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

pqs = session.query(PQ).all()

for pq in pqs:
	print pq.file_name
	buffer = open(pq.file_name).read()

	pattern = r'((.*\n){2})(\(No\.[\s]*B\/81*\))'
	regex = re.compile(pattern, re.DOTALL)
	for match in regex.finditer(buffer):
		print match.group(1)
	# with open(pq.file_name) as f:
	# 	for i, line in enumerate(f, 1):
	# 		if i == 23:
	# 			print "found the line"
	# 			break
	# 	print line





