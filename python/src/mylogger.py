import os
import logging.config

class MyLogger(object):

    # set logging to both file and screen
    def __init__(self):
        logging.config.fileConfig('../config/logging.conf')
        self.logger = logging.getLogger('scrapeforum')
        self.logger.addHandler(logging.StreamHandler())
        self.errorIndicated = False

    def isErrorIndicated(self):
        return self.errorIndicated

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
        self.errorIndicated = True

    def critical(self, msg):
        self.logger.critical(msg)
        self.errorIndicated = True

    def fatal(self, msg):
        self.logger.fatal(msg)
        self.errorIndicated = True


