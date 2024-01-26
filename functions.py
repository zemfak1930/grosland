from geoalchemy2 import WKTElement

from geomet import wkt

from grosland.app import session
from grosland.models import Cadastre, Archive

import time


def get_parcels(koatuu: str, layer: str = 'cadastre', write: bool = False):
    """
        Accepts a KOATUU and returns a list of cadastre/archive objects of the required KOATUU.
        Additionaly creates a file with a list of the cadastre/archive in a given KOATUU.
        :params  koatuu: e.q. '5121680800' --> Search parameter by layer,
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


def create_db_object(**kwargs):
    """
        Accepts a dictionary with parameters required to execute the function.
        Reads geojson file and adds objects to database.
        Only for Cadastre or Archive classes.
    :param kwargs: {
        "file": str = path to .geojson file,
        "layer: str = "cadastre" or "archive",

        "cadnum": str = column name in the .geojson file to communicate with the class,
        "ownership_code": str,
        "purpose_code": str,
        "area": str,
    }
    :return: None
    """
    model = Cadastre if kwargs["layer"] == "cadastre" else (Archive if kwargs["layer"] == "archive" else None)

    if model:
        geojson = eval(open(kwargs["file"]).read().replace("null", "None"))

        for item in geojson["features"]:
            new_object = model(
                cadnum=item["properties"][kwargs["cadnum"]],
                ownership_code=str(item["properties"][kwargs["ownership_code"]]),
                purpose_code=str(item["properties"][kwargs["purpose_code"]]),
                area=item["properties"][kwargs["area"]],
                address=item["properties"][kwargs["address"]],
                geometry=WKTElement(wkt.dumps({
                    "type": item["geometry"]["type"],
                    "coordinates": item["geometry"]["coordinates"]
                }), srid=4326)
            )

            session.add(new_object)
        session.commit()


def list_comparison(services_file: str, grosland_file: str):
    """
        Generates lists of plots that need to be removed or added to the database.
    :param services_file: Path to the file with plot from Geocadastre services.
    :param grosland_file: Path to the file with plot from grosland.
    :return: None
    """
    services = set(open(services_file).read().split("\n"))
    cadastre = set(open(grosland_file).read().split("\n"))

    del_plot = open("temp/del_plot.txt", "a")
    add_plot = open("temp/add_plot.txt", "a")

    for item in cadastre:
        if item not in services:
            del_plot.write(f"{item}\n")
    del_plot.close()

    for i in services:
        if i not in cadastre:
            add_plot.write(f"{i}\n")
    add_plot.close()


def transfer_to_archive(file):
    """
        Transferring areas to the archive layer.
    :param file: Path to the file.
    :return: None
    """
    delete_list = set(open(file).read().split("\n"))

    for item in delete_list:
        cadastre = session.query(Cadastre).filter_by(cadnum=item).first()

        archive = Archive(
            cadnum=cadastre.cadnum,
            ownership_code=cadastre.ownership_code,
            purpose_code=cadastre.purpose_code,
            area=cadastre.area,
            address=cadastre.address,
            geometry=cadastre.geometry
        )

        session.add(archive)
        session.delete(cadastre)
    session.commit()

