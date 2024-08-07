from grosland.app import app
from grosland.blueprints import api, cadastral_map, ascm_map
import grosland.main


def create_app():
    app.register_blueprint(api)
    app.register_blueprint(cadastral_map)
    app.register_blueprint(ascm_map)

    return app
