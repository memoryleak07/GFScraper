import logging
import logging.handlers
import datetime
import sys

today = datetime.date.today() 
LOG_FILENAME = "GFScraper_{0}.log".format('%02d' % today.day) 
# create logger with 'spam_application'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1048576, backupCount=5)
handler2 = logging.StreamHandler(sys.stdout)
handler2.setLevel(logging.INFO)
logger.addHandler(handler)
# create file handler which logs even debug messages
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
handler2.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(handler2)
