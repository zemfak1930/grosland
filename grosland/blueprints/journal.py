from flask import request, Response
from grosland.models import History
from flask import Blueprint

from flask_security import login_required

from grosland.app import session


journal = Blueprint("journal", __name__, url_prefix="/journal")


@journal.route("/")
@login_required
def index():
    """
        Main page for journal.
    :return:
    """
    return "Blueprint journal home page"


@journal.route("/search_history/", methods=["POST"])
@login_required
def search_history():
    """
        Saving search history.
    """
    session.add(History(message=request.get_data().decode()))
    session.commit()
    return Response(status=200)
