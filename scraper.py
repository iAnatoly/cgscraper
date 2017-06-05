""" Scrapes a certain forum for new posts containing certain keywords """
import re
import json
import smtplib
import sys
import os
from email.mime.text import MIMEText

import requests
from lxml import html


reload(sys)
sys.setdefaultencoding('utf-8')

MAX_PAGE_NUM = 10

class Scraper(object):
    """ Implements the scraping for certain website. Config is injected into constructor. """

    def __init__(self, config):
        self.config = config

    def send_email(self, result):
        """ sends a well-formatted email over authenticates TLS SMTP connection. """

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

        except Exception as ex:
            print("\nError sending out email: {0}.".format(ex))
            raise ex

    def fetch_content(self, pagenum):
        """ Fetches content for a specific page on the forum. """
        print('Fetching page {}'.format(pagenum))
        url_template = self.config['url_template']
        url = url_template.format(pagenum)
        page = requests.get(url)
        return page.content

    def scrape(self):
        """ Implements scraping algorithm. """

        first = None
        if os.path.exists('scraper.last'):
            with open('scraper.last') as marker_file:
                last = marker_file.readline().strip()
        else:
            last = None

        print('last: "{}"'.format(last))

        targets = []
        for target in self.config['scraping_targets']:
            targets.append(re.compile(target, flags=re.IGNORECASE))

        pagenum = 1
        current_post_id = None

        while True:

            content = self.fetch_content(pagenum)
            tree = html.fromstring(content)

            postings = tree.xpath('//td[starts-with(@id,"td_threadtitle_")]')

            if not postings:
                print("no more posts")
                break

            for posting in postings:
                current_post_id = posting.get('id')
                title = posting.get('title').replace('\n', '')

                if current_post_id == last:
                    print("done")
                    break

                for regex in targets:
                    if regex.search(title):
                        print('*** MATCH ***')
                        print(title)
                        self.send_email(title)

                if not first and title.startswith('Make:'):
                    first = current_post_id

            if current_post_id == last or pagenum>MAX_PAGE_NUM:
                print("and done")
                break

            pagenum += 1

        if first:
            print('saving {} as current position'.format(first))
            with open('scraper.last', 'w') as marker_file:
                marker_file.write(first)


def main():
    """ Reads config, instantiates scraper, runs scraper """
    with open('scraper.config.json') as json_data_file:
        config = json.load(json_data_file)

    # override password through an env variable:
    config['email']['smtp']['pass'] = os.getenv('SCRAPER_SMTP_PASS', config['email']['smtp']['pass'])

    scraper = Scraper(config)
    scraper.scrape()

if __name__ == '__main__':
    main()
