from flask import Blueprint, jsonify, request, Response
from flask_security import login_required, current_user
from grosland.app import cache, session
from grosland.models import Cadastre, Archive, Land, Ownership, Purpose, History


api = Blueprint('api', __name__, url_prefix="/api")


#   Main page of API   -------------------------------------------------------------------------------------------------
@api.route("/")
@login_required
@cache.cached()
def index():
    """
        Main page for api.
    :return:
    """
    return "Blueprint api home page"


#   GET data    --------------------------------------------------------------------------------------------------------
@api.route("/user", methods=["GET"])
@login_required
def user():
    return jsonify({"email": current_user.email})


@api.route("/parameters", methods=["GET"])
@login_required
@cache.cached()
def parameters():
    result = {}

    for model in (Ownership, Purpose):
        result[model.__tablename__] = {}

        for item in session.query(model).all():
            result[item.__tablename__][item.code.replace(".", "") + item.__tablename__.title() + "CustomParameter"] = {
                "code": item.code,
                "desc": item.desc
            }

    return jsonify(result)


#   CREATE data --------------------------------------------------------------------------------------------------------
@api.route("/history", methods=["POST"])
@login_required
def history():
    """
        Saving search history.
    """
    session.add(History(message=request.get_data().decode()))
    session.commit()
    return Response(status=200)
