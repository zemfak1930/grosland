from flask import abort, Blueprint, jsonify, request

from flask_security import login_required, current_user

from grosland.app import session
from grosland.models import Cadastre, Archive, Land

from geoalchemy2.shape import from_shape

from shapely.geometry import shape


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


@api.route("/lands", methods=["POST"])
@login_required
def create_polygon():
    count = session.query(Land.id).order_by(Land.id.desc()).first()

    new_polygon = Land(
        cadnum=count[0] + 1 if count is not None else 1,
        area=float(request.json["area"]),
        ownership_code="0",
        purpose_code="0",
        geometry=from_shape(shape({
            "type": "MULTIPOLYGON",
            "coordinates": [eval(request.json["geojson"])["geometry"]["coordinates"]]
        }), srid=4326),
        note=current_user.email
    )

    session.add(new_polygon)
    session.commit()

    return "200"


@api.route("/lands", methods=["DELETE"])
@login_required
def delete_polygon():
    land = session.query(Land).filter_by(
        cadnum=request.json.get('cadnum', None)
    ).first()

    session.delete(land)
    session.commit()

    return "200"


@api.route("/email", methods=["GET"])
@login_required
def user_email():
    return jsonify({"email": current_user.email})
