from lastbatch import LastBatch

#lastBatch = LastBatch()
#for topic in lastBatch.getProcessedSet():
#    print(topic)



import logging.config

logging.config.fileConfig('../config/logging.conf')

# create logger
logger = logging.getLogger('scrapeforum')
logger.addHandler(logging.StreamHandler())

