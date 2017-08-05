import re, string
from pdf2txt import convert_pdf_to_txt
from os import remove, listdir
from os.path import isfile, join, exists
from datetime import datetime, timedelta

all_files = [f for f in listdir('./pdf') if isfile(join('./pdf', f))]

#if exists(join('./pdf','.DS_Store')):
#	remove(join('./pdf','.DS_Store'))

"""
for file in all_files:
	original_file = join('./pdf', file)
	text_output = convert_pdf_to_txt(original_file)
	write_path = join('./txt', re.sub('.pdf', '.txt', file))
	with open(write_path, "w+") as f:
		f.write(text_output)
		f.close()
"""

pattern = r'((\(No\.[\s]*B\/[0-9]*\))(.*?)asked(.*?)whether(.*?)\.(.*?))'

# buffer = open('./txt/20141222.txt').read()

all_text_files = [f for f in listdir('./txt') if isfile(join('./txt', f))]

if exists(join('./txt','.DS_Store')):
	remove(join('./txt','.DS_Store'))

regex = re.compile(pattern, re.DOTALL)
pqs = []
pq = dict()
pq_refs = []

for file in all_text_files:
	text_file = join('./txt', file)
	date_str = re.sub('.txt','', file)
	date = datetime(year=int(date_str[0:4]), month=int(date_str[4:6]), day=int(date_str[6:8]))

	buffer = open(join('./txt', file)).read()

	for match in regex.finditer(buffer):
		pq_refs.append({"file": file, "pq_ref": match.group(2)})
		# pqs.append({"PQ ref": match.group(2), "Date": date.strftime("%B %d, %Y"), "From": match.group(3), "To": match.group(4), "PQ": match.group(1)})

for pq in pq_refs:
	buffer = open(join('./txt', pq['file'])).read()
	pos = re.search(pq['pq_ref'], buffer).start()
	pq['pos'] = pos
	print pq['file'], pq['pq_ref'], pq['pos']
	title = buffer[ pq['pos']-100 : pq['pos']-1 ]
	print title.translate(None, string.ascii_lowercase)
	print '-----------------------------------'

