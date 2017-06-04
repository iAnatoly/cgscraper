from lxml import html
import requests
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

first = None
with open('scraper.last') as f:
	last = f.readline().strip()

print('last: "{}"'.format(last))

url = 'https://www.calguns.net/calgunforum/forumdisplay.php?f=332&order=desc&page={}'
targets = [
	re.compile('cz.*shadow', flags=re.IGNORECASE), 
	re.compile('tactical\s+sport', flags=re.IGNORECASE), 
	re.compile('tacsport', flags=re.IGNORECASE), 
	re.compile('cz.*75.*ts', flags=re.IGNORECASE),
	re.compile('sig.*226', flags=re.IGNORECASE)
]

pagenum = 1
while(True):
	print('Fetching page {}'.format(pagenum))
	page = requests.get(url.format(pagenum))
	content = page.content #.decode('ISO-8859-1') #.encode('ascii', 'ignore')
	tree = html.fromstring(content)

	postings = tree.xpath('//td[starts-with(@id,"td_threadtitle_")]')
	
	if not postings:
		print("no more posts")
		break

	for posting in postings:
		# .get('title')
		# 'Make: Eaa (Tanfoglio) \n \nModel: Stock 2 \n \nCaliber: 9mm  \n \nLocation (city or county): Santa Clara \n \nPrice: $1950'
		id = posting.get('id')
		title = posting.get('title').replace('\n','')

		if id == last:
			print("done")
			break

		#if not title.startswith('Make:'):
		#	print ('Skipping: {}'.format(str(title[:20])))
		#	continue
		
		for regex in targets:
			if regex.search(title):
				print('*** MATCH ***')
				print(title)

		if not first and title.startswith('Make:'):
			first = id			

	
	if id == last:
		print("done")
		break

	pagenum += 1

if first:
	with open('scraper.last','w') as f:
		print('saving {} as current position'.format(first))
		f.write(first)
