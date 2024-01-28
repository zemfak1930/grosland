from flask import render_template

from flask_security import login_required

from grosland.app import app, session


#   Map ----------------------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET"])
@login_required
def index():
    """
        Display a map with layers.
    """
    return render_template("index.html")


#   Event   ------------------------------------------------------------------------------------------------------------
@app.teardown_appcontext
def shutdown_session(exception=None):
    """
        Fixed error sqlalchemy.exc.TimeoutError
    """
    session.remove()
