from flask_security import login_required

from grosland.app import app, session


@app.route("/")
@login_required
def index():
    return "Все ОК"


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()
