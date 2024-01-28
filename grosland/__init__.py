from grosland.app import app
from grosland.blueprints import api, journal
import grosland.main


def create_app():
    app.register_blueprint(api)
    app.register_blueprint(journal)

    return app
