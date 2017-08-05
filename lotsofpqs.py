
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

pattern = r'((\(No\.[\s]*B\/[0-9]*\))(.*?)asked(.*?)whether(.*?)\.(.*?))'

# buffer = open('./txt/20141222.txt').read()

all_text_files = [f for f in listdir('./txt') if isfile(join('./txt', f))]

# all_text_files.remove('.gitkeep')

if exists(join('./txt','.DS_Store')):
	remove(join('./txt','.DS_Store'))

regex = re.compile(pattern, re.DOTALL)
pqs = []
pq = dict()

total = len(all_text_files)

for i, file in enumerate(all_text_files):
	text_file = join('./txt', file)
	date_str = re.sub('.txt','', file)
	date = datetime(year=int(date_str[0:4]), month=int(date_str[4:6]), day=int(date_str[6:8]))
	session1 = Session(date=date)
	session.add(session1)
	session.flush()
	session_id = session1.id
	new_session = session.query(Session).filter_by(id=session_id).one()
	print "%i of %i: %s"%(i, total, file)
	buffer = open(join('./txt', file)).read()
	for match in regex.finditer(buffer):
		# pqs.append({"PQ ref": match.group(2), "Date": date.strftime("%B %d, %Y"), "From": match.group(3), "To": match.group(4), "PQ": match.group(1)})
		pos = re.search(match.group(2), buffer).start()
		title = buffer[ pos-100 : pos-1 ]
		title = re.sub('[a-z]','',title)
		asked_by = unicode(match.group(3), "utf-8")
		asked_by = asked_by.replace("\n", "")
		asked_by = ' '.join(filter(None,asked_by.split(' ')))
                print asked_by
		if (asked_by.index('(')):
			asked_pattern = asked_by.index('(')
		else:
			break
		tit = asked_by[asked_pattern+1:]
		tit = tit[:-1]

		deputies = session.query(Deputy).all()
		for dep in deputies:
			if (dep.title==tit):
				id = dep.id

		deputy = session.query(Deputy).filter_by(id=id).one()

		answer = buffer[ pos+len(match.group(1)): pos+len(match.group(1))+50000 ]
		ref = r'(\(No\.[\s]*B\/[0-9]*\))'
		end_point = answer.find('(No. B/')
		exp = re.compile(ref)
		if (re.search(exp, answer) is not None):
			end_point = re.search(exp, answer).start()
			answer = answer[1:end_point]

		pq1 = PQ(title=unicode(title,"utf-8", errors='ignore'), pq_ref=unicode(match.group(2), "utf-8", errors='ignore'), session=new_session, deputy=deputy,
					file_name=text_file, 
					answer = unicode(answer,"utf-8",errors='ignore'),
					pq=unicode(match.group(1), "utf-8", errors='ignore'), 
					date_asked=unicode(date.strftime("%B %d, %Y"), "utf-8", errors='ignore'), 
					asked_by=asked_by, 
					asked_to=unicode(match.group(4), "utf-8", errors='ignore')
				)
		session.add(pq1)
		session.commit()
