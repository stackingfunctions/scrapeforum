import smtplib
import constants
from configurator import Configurator


# TODO rework it to proper inheritance
class Mailer(object):

    def __init__(self, type=constants.EMAIL_NOTIFICATION):

        self.type = "Error" if type == constants.EMAIL_ERROR else "Notification"

        configurator = Configurator()

        self.emailAccount = configurator.getEmailAccount()
        self.emailSender = configurator.getEmailSender()
        self.emailReceivers = configurator.getEmailReceivers(type)

        self.sender = self.emailSender['sender_email']
        self.receiver_emails = self.emailReceivers['receiver_emails'].replace(" ", "").split(',')
        self.receiver_names = self.emailReceivers['receiver_names'].replace(" ", "").split(',')

        self.subjectPrefix = "[ERROR] " if type == constants.EMAIL_ERROR else "[NOTIFY] "

    def createReceivers(self):
        receivers = ""
        for(name, email) in zip(self.receiver_names, self.receiver_emails):
            receivers += name + """<""" + email + """>, """
        return receivers[:-2]

    def send(self, subject, message):
        message2send = """From: """ + self.emailSender['sender_name'] + """ <""" + self.emailSender['sender_email'] + """>
To: """ + self.createReceivers() + """
Subject: """ + self.subjectPrefix + subject + """

""" + message

        try:
            smtpObj = smtplib.SMTP_SSL(self.emailAccount['server'])
            smtpObj.login(self.emailAccount['user'], self.emailAccount['passwd'])
            smtpObj.sendmail(self.sender, self.receiver_emails, message2send)
            print ("Sent email")
        except smtplib.SMTPException:
            # TODO: Log in DB
            print ("Error: unable to send email")
        finally:
            smtpObj.quit()

