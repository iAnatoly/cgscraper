from lxml import html
from email.mime.text import MIMEText

import requests
import re
import json

import smtplib

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def sendEmail(result):
	with open('config.json') as json_data_file:
    		config = json.load(json_data_file)

	recipients = config['recipients']
	subject = config['subject']
	mail_from = config['sender']
	smtpserver = config['smtp']['server']
	smtpuser = config['smtp']['user']
	smtppass = config['smtp']['pass']

        try:
            server = smtplib.SMTP(smtpserver)
            server.set_debuglevel(False)
            server.ehlo()
            server.starttls()
            server.login(smtpuser, smtppass)

            msg = MIMEText(result, 'plain')
            msg['Subject'] = subject
            msg['From'] = 'Calguns Scraper <{}>'.format(mail_from)
            msg['To'] = ';'.join(recipients)

            server.sendmail(mail_from, recipients, msg.as_string())

            server.quit()

        except Exception as e:
            print "\nError sending out email: {0}.".format(e)
	    raise e

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
]

pagenum = 1
while(True):
	print('Fetching page {}'.format(pagenum))
	page = requests.get(url.format(pagenum))
	content = page.content 
	tree = html.fromstring(content)

	postings = tree.xpath('//td[starts-with(@id,"td_threadtitle_")]')
	
	if not postings:
		print("no more posts")
		break

	for posting in postings:
		id = posting.get('id')
		title = posting.get('title').replace('\n','')

		if id == last:
			print("done")
			break

		for regex in targets:
			if regex.search(title):
				print('*** MATCH ***')
				print(title)
				sendEmail(title)

		if not first and title.startswith('Make:'):
			first = id			

	
	if id == last:
		print("and done")
		break

	pagenum += 1

if first:
	print('saving {} as current position'.format(first))
	with open('scraper.last','w') as f:
		f.write(first)
