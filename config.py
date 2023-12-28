from dotenv import load_dotenv

import os
from os.path import join, dirname


load_dotenv(join(dirname(__file__), '.env'))


class Config:
    #   Flask ----------------------------------------------------------------------------------------------------------
    DEVELOPMENT = True
    DEBUG = True

    #   SECRET ---------------------------------------------------------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SECURITY_PASSWORD_HASH = os.environ.get("SECURITY_PASSWORD_HASH")
