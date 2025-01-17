from flask import render_template
from flask_security import login_required
from grosland.app import app, session
from grosland.models import Updates


#   Main routes --------------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET"])
@login_required
def index():
    """
        Display menu for map selection.
    """
    return render_template("index.html")


@app.route("/updates", methods=["GET"])
@login_required
def show_updates():
    """
        List of recent portal updates.
    """
    return render_template("updates.html", updates=session.query(Updates).order_by(Updates.date.desc()))


#   Event   ------------------------------------------------------------------------------------------------------------
@app.teardown_appcontext
def shutdown_session(exception=None):
    """
        Fixed error sqlalchemy.exc.TimeoutError
    """
    session.remove()
