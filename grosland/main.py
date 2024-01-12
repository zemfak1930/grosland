from grosland.models import Cadastre

from flask import render_template, request, jsonify

from flask_security import login_required

from grosland.app import app, session


#   Map ----------------------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """
        Display a map with layers and search for a specific area.
    """
    if request.method == "POST":
        geojson = session.query(Cadastre.geometry.ST_AsGeoJSON()).filter_by(
            cadnum=request.form.to_dict()["cadnum"]
        ).first()

        if geojson:
            return jsonify({
                "coordinates": eval(geojson[0])["coordinates"]
            })

    return render_template("index.html")


#   Event   ------------------------------------------------------------------------------------------------------------
@app.teardown_appcontext
def shutdown_session(exception=None):
    """
        Fixed error sqlalchemy.exc.TimeoutError
    """
    session.remove()
