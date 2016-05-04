import smtplib
from email.mime.text import MIMEText

class Mailer:
    def __init__(self, From, to, host, port, user, password, logger):
        self.smtp = smtplib.SMTP_SSL(host, port)
        self.user = user
        self.password = password
        self.From = From
        self.to = to
        self.logger = logger

    def send(self, subject, content, mime = 'html'):
        msg = MIMEText(content, mime, 'utf-8')

        msg['Subject'] = subject
        msg['From'] = self.From
        msg['To'] = self.to

        try:
            self.logger.info('sending email (%s) from %s to %s' % (subject, self.From, self.to))
            self.smtp.login(self.user, self.password)
            self.smtp.sendmail(self.From, self.to, msg.as_string())
        finally:
            self.smtp.quit()
