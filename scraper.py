from lxml import html
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

first = None
with open('scraper.last') as f:
	last = f.readline().strip()

print('last: "{}"'.format(last))

url = 'https://www.calguns.net/calgunforum/forumdisplay.php?f=332&order=desc&page={}'
targets = ['tactical\s+sport', 'cz.*75.*ts']

pagenum = 1
while(True):
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

		if not title.startswith('Make:'):
			print ('Skipping: {}'.format(str(title[:20])))
			continue

		print(id, title)

		if not first and title.startswith('Model:'):
			first = id			
	
	if id == last:
		print("done")
		break

	pagenum += 1


with open('scraper.last','w') as f:
	print('saving {} as current position'.format(first))
	f.write(first)
