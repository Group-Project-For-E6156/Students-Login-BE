import os


class BaseConfig(object):
    """Base Configuration"""
    # main config
    SECRET_KEY = 'my_precious'
    SECURITY_PASSWORD_SALT = 'my_precious_two'
    DEBUG = False

    # mail settings
    MAIL_SERVER = 'smtp.qq.com'
    # qq mail authentication
    MAIL_USERNAME = os.environ['APP_MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['APP_MAIL_PASSWORD']

    # mail account
    SENDER_NAME = 'TEAMMATCHER TEAM'