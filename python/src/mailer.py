from configurator import Configurator
from metadata import ScrapeError
import smtplib
import constants
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# TODO rework it to proper inheritance
class Mailer(object):
    """A mailer object which has type either NOTIFICATION or ERROR. Both types have different recepients configured in config.ini """

    def __init__(self, type=None):

        self.type = "Error" if type == constants.EMAIL_TYPE_ERROR else "Notification"

        # Get configuration values from Configurator
        configurator = Configurator()

        # Get configuration groups for email account, sender and receivers
        self.emailAccount = configurator.getEmailAccount()
        self.emailSender = configurator.getEmailSender()
        self.emailReceivers = configurator.getEmailReceivers(type)

        # Configure sender and receivers
        self.sender = self.emailSender['sender_email']
        self.receiver_emails = self.emailReceivers['receiver_emails'].replace(" ", "").split(',')
        self.receiver_names = self.emailReceivers['receiver_names'].replace(" ", "").split(',')

        self.subjectPrefix = "[ERROR] " if type == constants.EMAIL_TYPE_ERROR else "[NOTIFY] "

    def createReceivers(self):
        """Construct the receivers string as [name] <[]email]@[host.topdomain]>.
        Just like: "Gergo <gergo@imnottelling.com>, Error <[error]@[anotherhost.topdomain]>" """
        receivers = ""
        for(name, email) in zip(self.receiver_names, self.receiver_emails):
            receivers += name + """<""" + email + """>, """
        return receivers[:-2]

    def send(self, subject, message, **kwargs):
        """Sends email and logs error in DB if session and batch_id are passed in as named arguments"""

        if Configurator().getEmailEnabled():

            # Construct email message
            message2send = """From: """ + self.emailSender['sender_name'] + """ <""" + self.emailSender['sender_email'] + """>
To: """ + self.createReceivers() + """
Subject: """ + self.subjectPrefix + subject + """

""" + message

            # Try to send email
            try:
                smtpObj = smtplib.SMTP_SSL(self.emailAccount['server'])
                smtpObj.login(self.emailAccount['user'], self.emailAccount['passwd'])
                smtpObj.sendmail(self.sender, self.receiver_emails, message2send)
                # TODO: replace with MyLogger
                print ("Sent email")
            except smtplib.SMTPException:
                session = kwargs.get("session")
                batch_id = kwargs.get("batch_id")
                if session and batch_id:
                    # Log error in DB
                    session.add(ScrapeError(batchId=batch_id, errorType=constants.ERR_EMAIL_SMTP_ERROR,
                                            errorString=constants.ERR_EMAIL_SMTP_ERROR_STR))

                # TODO: replace with MyLogger
                print ("Error: unable to send email")
            finally:
                smtpObj.quit()


    # TODO: implement sending email with error log attached
#    def sendWithAtachment(self, subject, message):
#        msg = MIMEMultipart()
#        msg['Subject'] = subject
#        msg['From'] = self.emailSender['sender_name'] + """ <""" + self.emailSender['sender_email'] + """>"""
#        msg['To'] = self.createReceivers()
#        with open('../../log/scrapeforum.log', 'rb') as attachment:
#            log = MIMEText(attachment.read().encode('utf-8'))
#        msg.attach(log)


#        smtpObj = smtplib.SMTP_SSL(self.emailAccount['server'])
#        smtpObj.login(self.emailAccount['user'], self.emailAccount['passwd'])
#        smtpObj.send_message(msg)
#        smtpObj.quit()

#        s = smtplib.SMTP(host, 143)
#        s.send_message(msg)
#        s.quit()