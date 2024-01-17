from grosland.app import session
from grosland.models import Cadastre, Archive

import time


def get_parcels(koatuu: str, layer: str = 'cadastre', write: bool = False):
    """
        Accepts a KOATUU and returns a list of cadastre/archive objects of the required KOATUU.
        Additionaly creates a file with a list of the cadastre/archive in a given KOATUU.
        :param  koatuu: e.q. '5121680800' --> Search parameter by layer,
                layer: 'cadastre' or 'archive' --> In which layer to look for data,
                write: bool --> Whether to write data to file or not.
        :return: [object, object, ...]
    """
    #   Search model definition
    model = Cadastre if layer == 'cadastre' else (Archive if layer == 'archive' else None)

    #   Database search
    cadastre_list = (
        session.query(model).filter(model.cadnum.like(f'{koatuu[0:8]}%')).order_by(model.cadnum.asc()).all()
    )

    #   Writing data to a file. Optional
    if write:
        with open(f"temp/{layer}_{koatuu[0:8] + '00'}_{int(time.time())}.txt", "a") as file:
            for cadastre in cadastre_list:
                file.write(f'{cadastre.cadnum}\n')

    return cadastre_list
