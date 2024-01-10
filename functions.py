from grosland.app import session
from grosland.models import Cadastre


def get_cadastre(koatuu: str):
    """
        Accepts a KOATUU and returns a list of cadastral objects of the required KOATUU.
        Additionaly creates a list of cadastre in a given KOATUU.
        :param koatuu: e.q. 5121680800
        :return: [object, object, ...]
    """
    cadastre_list = (
        session.query(Cadastre).filter(Cadastre.cadnum.like(f'{koatuu[0:8]}%')).order_by(Cadastre.cadnum.asc()).all()
    )

    with open(f"temp/{koatuu[0:8] + '00'}.txt", "a") as file:
        for cadastre in cadastre_list:
            file.write(f'{cadastre.cadnum}\n')

    return cadastre_list
