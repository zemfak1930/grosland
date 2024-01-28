from flask import abort, Blueprint, jsonify, request

from flask_security import login_required

from grosland.app import session
from grosland.models import Cadastre, Archive


api = Blueprint('api', __name__, url_prefix="/api")


@api.route("/")
@login_required
def index():
    """
        Main page for api.
    :return:
    """
    return "Blueprint api home page"


@api.route("/parcels/", methods=["GET"])
@login_required
def get_parcels_list():
    """
        Get a list of all generated land areas in the database.
    :return: {
        "Archive":  ["5121680800:01:001:0981", "5121680800:01:001:1000", ...],
        "Cadastre": ["5121680800:01:001:0025", "5121680800:01:001:0026", ...]
    }
    """
    parcels = {}
    base_operator = ["==", ">=", "<=", "!="]
    arg_area = None

    for model in [Cadastre, Archive]:
        query_filter = []

        for item in ["cadnum", "area", "ownership_code", "purpose_code", "address"]:
            if request.args.get(item):
                #   Params "area"   ------------------------------------------------------------------------------------
                if item == "area":
                    area = request.args.get(item)
                    operator = area[:2]

                    try:
                        arg_area = float(area[2:].replace(",", "."))
                    except ValueError:
                        pass

                    if operator in base_operator and arg_area and arg_area >= 0:
                        for op in base_operator:
                            if op == operator:
                                query_filter.append(
                                    eval(f"model.{item} {operator} {str(arg_area)}")
                                )

                #   Params "cadnum" / "ownership_code" / "purpose_code" / "address" ------------------------------------
                else:
                    query_filter.append(
                        eval(
                            f"model.{item}.ilike('" +
                            ("%" if item in ["address", "cadnum"] else "") +    # If we have address/cadnum parameter
                            f"{request.args.get(item)}%')"
                        )
                    )

        #   Run filter  ------------------------------------------------------------------------------------------------
        parcels.update({
            model.__name__: [
                item.cadnum for item in session.query(model).filter(*query_filter).order_by(model.cadnum.asc()).all()
            ]
        })

    return jsonify(parcels)


@api.route("/parcels/<cadnum>/",  methods=["GET"])
@login_required
def get_parcel(cadnum):
    """
         Search for land area by cadastral and archive layers.
    :return: Information about land area in geojson format or Error "404 PAGE NOT FOUND"
    """
    for model in [Cadastre, Archive]:
        parcel = session.query(model).filter_by(cadnum=cadnum).first()

        if parcel:
            return jsonify(parcel.wkb_to_geojson())

    return abort(404)
