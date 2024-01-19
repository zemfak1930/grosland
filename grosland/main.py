from flask import render_template, request, jsonify, Response

from flask_security import login_required

from grosland.app import app, session
from grosland.models import Cadastre, History


#   Map ----------------------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET"])
@login_required
def index():
    """
        Display a map with layers.
    """
    return render_template("index.html")


@app.route("/get_coordinates", methods=["POST"])
@login_required
def get_coordinates():
    """
        Get coordinates of the land area.
    """
    geojson = session.query(Cadastre.geometry.ST_AsGeoJSON()).filter_by(
        cadnum=request.form.to_dict()["cadnum"]
    ).first()

    return jsonify({"coordinates": eval(geojson[0])["coordinates"]}) if geojson else Response(status=404)


@app.route("/history", methods=["POST"])
@login_required
def history():
    """
        Saving search history.
    """
    session.add(History(cadnum=request.get_data().decode()))
    session.commit()
    return Response(status=200)


#   Event   ------------------------------------------------------------------------------------------------------------
@app.teardown_appcontext
def shutdown_session(exception=None):
    """
        Fixed error sqlalchemy.exc.TimeoutError
    """
    session.remove()
