from config import Config

from flask import Flask

from flask_admin import Admin

from flask_caching import Cache

from flask_security import Security, SQLAlchemySessionUserDatastore

from grosland.dictionary import main_dictionary

from grosland.models import *

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


#   Flask --------------------------------------------------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)


#   Flask-Caching ------------------------------------------------------------------------------------------------------
cache = Cache(
    app=app,
    config={
        "CACHE_TYPE": "simple",
        "CACHE_DEFAULT_TIMEOUT": 3600
    }
)


#   SQLAlchemy ---------------------------------------------------------------------------------------------------------
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(bind=engine)
session = scoped_session(sessionmaker(bind=engine))
Base.query = session.query_property()


#   Flask-Security -----------------------------------------------------------------------------------------------------
datastore = SQLAlchemySessionUserDatastore(session, Users, Roles)
security = Security(app, datastore)


#   Flask-Admin --------------------------------------------------------------------------------------------------------
admin = Admin(app, index_view=AdminView())
main_dictionary.update({"Main": ("Users", "History", "Revision", "Updates")})

for key, value in main_dictionary.items():
    for _ in value:
        eval(f"admin.add_view({_}View({_}, session, category='{key}'))")
