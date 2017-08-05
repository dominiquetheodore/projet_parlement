
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import PQ, Base, Deputy, Session, PNQ
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

pattern = r'qqqqq'
pattern2 = r'aaaaa'

# buffer = open('./txt/20141222.txt').read()

all_text_files = [f for f in listdir('./pnq') if isfile(join('./txt', f))]

# all_text_files.remove('.gitkeep')

if exists(join('./pnq','.DS_Store')):
	remove(join('./pnq','.DS_Store'))

regex = re.compile(pattern, re.DOTALL)
regex2 = re.compile(pattern2, re.DOTALL)
pqs = []
pq = dict()

total = len(all_text_files)

for i, file in enumerate(all_text_files):
	print "%i of %i: %s"%(i, total, file)
	text_file = join('./pnq', file)
	date_str = re.sub('.txt','', file)
	date = datetime(year=int(date_str[0:4]), month=int(date_str[4:6]), day=int(date_str[6:8]))
	buffer = open(join('./pnq', file)).read()
	for match in regex.finditer(buffer):
		pos = re.search(match.group(0), buffer).start()
		title = buffer[0:pos-1]

	for match in regex2.finditer(buffer):
		pos1 = re.search(match.group(0), buffer).start()
		pos2 = re.search(match.group(0), buffer).end()
		question = buffer[pos+5:pos1]
		answer = buffer[pos2:]
	
	sessions = session.query(Session).all()
	for sess in sessions:
		if sess.date.strftime('%d-%m-%Y') == date.strftime('%d-%m-%Y'):
			current_session = session.query(Session).filter_by(id=sess.id).one()
			break
			
	pnq = PNQ(title=unicode(title,"utf-8",errors='ignore'),
					file_name=text_file, 
					answer = unicode(answer,"utf-8",errors='ignore'),
					pnq=unicode(question, "utf-8",errors='ignore'), 
					session=current_session, 
				)
	session.add(pnq)
	session.commit()
	print 'PNQs added'
	
