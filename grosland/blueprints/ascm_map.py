from flask import Blueprint, render_template
from flask_security import login_required, roles_required

ascm_map = Blueprint("ascm_map", __name__, url_prefix="/ascm_map")


#   View ASCM map  -----------------------------------------------------------------------------------------------------
@ascm_map.route("/", methods=["GET"])
@login_required
@roles_required("ascm_map")
def index():
    """
        Display Alberta Survey Control Markers map.
    """
    return render_template("ascm_map.html")


