import logging
from config import LOGPATH, LOG_FILENAME
from utils.cloudwatchlogs_handler import CloudWatchLogsHandler

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - (%(filename)s at %(lineno)d)')

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# add formatter to ch
ch.setFormatter(formatter)
logger.addHandler(ch)

# Log to file
fileHandler = logging.FileHandler("{0}/{1}.log".format(LOGPATH, LOG_FILENAME))
fileHandler.setFormatter(formatter)
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

# Log to cloudwatchlogs
cloudwatchHandler = CloudWatchLogsHandler()
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(cloudwatchHandler)
