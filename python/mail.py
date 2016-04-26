import smtplib
from email.mime.text import MIMEText
from os import environ
import sys

content = sys.stdin.read()
msg = MIMEText(content, environ.get('MIME', 'html'), 'utf-8')

msg['Subject'] = sys.argv[1]
msg['From'] = environ.get('SMTP_FROM')
msg['To'] = environ.get('SMTP_TO')

s = smtplib.SMTP_SSL(environ.get('SMTP_HOST'), environ.get('SMTP_PORT'))
s.login(environ.get('SMTP_USER'), environ.get('SMTP_PASS'))
try:
    s.sendmail(environ.get('SMTP_FROM'), environ.get('SMTP_TO'), msg.as_string())
finally:
    s.quit()
