from lxml import html
from email.mime.text import MIMEText

import requests
import re
import json

import smtplib

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Scraper:
	def __init__(self,config):
		self.config = config

	def send_email(self, result):

		recipients = self.config['email']['recipients']
		subject = self.config['email']['subject']
		mail_from = self.config['email']['sender']
		smtpserver = self.config['email']['smtp']['server']
		smtpuser = self.config['email']['smtp']['user']
		smtppass = self.config['email']['smtp']['pass']

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
	
	def fetch_content(self, pagenum):
		print('Fetching page {}'.format(pagenum))
		url_template = self.config['url_template']
		url = url_template.format(pagenum)
		page = requests.get(url)
		return page.content 

	def scrape(self):
		first = None
		with open('scraper.last') as f:
			last = f.readline().strip()

		print('last: "{}"'.format(last))

		targets = []
		for target in self.config['scraping_targets']:
			targets.append(re.compile(target, flags=re.IGNORECASE))

		pagenum = 1

		while(True):

			content = self.fetch_content(pagenum)
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
						self.send_email(title)

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

def main():
	with open('scraper.config.json') as json_data_file:
		config = json.load(json_data_file)

	scraper = Scraper(config)
	scraper.scrape()	


main()
