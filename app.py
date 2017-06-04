""" Launcher/scheduler for opensift platform """
import os
import time
import scraper

RUN_PERIOD=600

if not os.getenv('SCRAPER_SMTP_PASS'):
    print("Missing scraper smtp password variable. Exiting.")
    exit(-1)

while True:
    print("Scaraping")
    scraper.main()

    print("Sleeping for {} seconds".format(RUN_PERIOD))
    time.sleep(RUN_PERIOD)
