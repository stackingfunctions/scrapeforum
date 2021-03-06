from configparser import ConfigParser
import constants

class Configurator:

    def __init__(self):
        self.config = ConfigParser()
        self.config.read('../config/config.ini')

    def getConfig(self):
        return self.config

    def getDb(self):
        return self.config['Destination DB']

    def getEmailAccount(self):
        return self.config['Email account']

    def getEmailSender(self):
        return self.config['Email sender']

    def getEmailReceivers(self, type):
        return self.config['Error email receivers'] if type == constants.EMAIL_TYPE_ERROR else self.config['Notification email receivers']

    def getURL(self):
        return self.config['Website']

    def getDbConnectionString(self):
        return "mysql://" + self.config['Destination DB']['user'] + ":" + self.config['Destination DB']['passwd'] + "@" + self.config['Destination DB']['host'] + "/" + self.config['Destination DB']['dbName'] + "?charset=" + self.config['Destination DB']['charset']

    def getEmailEnabled(self):
        return True if self.config['Email sending enabled'] == 'True' else False