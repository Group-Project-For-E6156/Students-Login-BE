from flask_mail import Message, Mail
from flask import Flask
from src.app import config

app = Flask(__name__)
app.config['MAIL_SERVER'] = config.BaseConfig.MAIL_SERVER
app.config['MAIL_PORT'] = config.BaseConfig.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.BaseConfig.MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = config.BaseConfig.MAIL_USE_SSL
app.config['MAIL_USERNAME'] = config.BaseConfig.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.BaseConfig.MAIL_PASSWORD
mail = Mail(app)


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=config.BaseConfig.MAIL_DEFAULT_SENDER
    )
    mail.send(msg)
