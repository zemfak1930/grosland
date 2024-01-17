from config import Config

from flask import Flask

from flask_admin import Admin

from flask_security import Security, SQLAlchemySessionUserDatastore

from grosland.models import *

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


#   Flask --------------------------------------------------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)


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

admin.add_category(name=("Layers", "Parameters",))
admin.add_views(
    UsersView(Users, session),
    HistoryView(History, session),

    LandView(Land, session, category="Layers"),
    CadastreView(Cadastre, session, category="Layers"),
    ArchiveView(Archive, session, category="Layers"),

    OwnershipView(Ownership, session, category="Parameters"),
    CategoryView(Category, session, category="Parameters"),
    PurposeView(Purpose, session, category="Parameters"),
)
