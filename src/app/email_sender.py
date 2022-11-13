from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from src.app.config import BaseConfig

host_server = BaseConfig.MAIL_SERVER
sender_mail = BaseConfig.MAIL_USERNAME
sender_passcode = BaseConfig.MAIL_PASSWORD


def send_mail(receiver='', mail_title='', mail_content=''):
    # ssl login
    smtp = SMTP_SSL(host_server)
    # set_debuglevel() for debug, 1 enable debug, 0 for disable
    # smtp.set_debuglevel(1)
    smtp.ehlo(host_server)
    smtp.login(sender_mail, sender_passcode)

    # construct message
    msg = MIMEText(mail_content, "html", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_mail
    msg["To"] = receiver
    smtp.sendmail(sender_mail, receiver, msg.as_string())
    smtp.quit()
