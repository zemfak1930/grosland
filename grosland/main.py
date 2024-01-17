from flask import render_template, request, jsonify

from flask_security import login_required

from grosland.app import app, session
from grosland.models import Cadastre, History


#   Map ----------------------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """
        Display a map with layers and search for a specific area.
    """
    if request.method == "POST":
        cadnum = request.form.to_dict()["cadnum"]
        geojson = session.query(Cadastre.geometry.ST_AsGeoJSON()).filter_by(cadnum=cadnum).first()[0]

        session.add(History(cadnum=cadnum))
        session.commit()

        if geojson:
            return jsonify({
                "coordinates": eval(geojson)["coordinates"]
            })

    session.add(History())
    session.commit()

    return render_template("index.html")


#   Event   ------------------------------------------------------------------------------------------------------------
@app.teardown_appcontext
def shutdown_session(exception=None):
    """
        Fixed error sqlalchemy.exc.TimeoutError
    """
    session.remove()
