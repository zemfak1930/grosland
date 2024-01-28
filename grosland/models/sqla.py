import datetime

from flask import request

from flask_security import UserMixin, RoleMixin, hash_password, current_user

from geoalchemy2 import Geometry

from shapely.wkb import loads

from sqlalchemy import ForeignKey, Column, String, Integer, DECIMAL, Boolean, Date, DateTime, event
from sqlalchemy.orm import DeclarativeBase, relationship, backref, declared_attr


__all__ = [
    "Base", "Users", "Roles", "History", "Revision", "Land", "Cadastre", "Archive", "Ownership", "Category", "Purpose"
]


#   Base ---------------------------------------------------------------------------------------------------------------
class Base(DeclarativeBase):
    """
        Base class for used in some models.
    """
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


#   Mixin --------------------------------------------------------------------------------------------------------------
class CodeDescMixin:
    """
        Adds code and description in some models.
    """
    code = Column(String, unique=True, nullable=False)
    desc = Column(String, nullable=False)

    def __str__(self):
        return self.desc


class GeometryMixin:
    """
        Base parameters for all polygonal objects.
    """
    area = Column(DECIMAL(12, 4), nullable=False)
    address = Column(String(255))
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)

    def wkb_to_geojson(self):
        """
            Convert WKBElement to Geojson format from polygonal object.
        :return: Geojson
        """
        polygons_coordinates = []

        for polygon in loads(bytes.fromhex(str(self.geometry))).geoms:
            exterior_coordinates = [list(coord) for coord in polygon.exterior.coords]
            interiors_coordinates = [[list(coord) for coord in interior.coords] for interior in polygon.interiors]
            polygons_coordinates.append([exterior_coordinates] + interiors_coordinates)

        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "id": self.id,
                    "area": float(self.area),
                    "address": self.address
                },
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": polygons_coordinates
                }
            }]
        }

        if self.__tablename__ in ["cadastre", "archive"]:
            geojson["features"][0]["properties"].update({
                "cadnum": self.cadnum,
                "category": self.purpose.category.code + " " + self.purpose.category.desc,
                "ownership": self.ownership_code + " " + self.ownership.desc + " власність",
                "purpose": self.purpose_code + " " + self.purpose.desc
            })

        elif self.__tablename__ in ["land"]:
            geojson["features"][0]["properties"].update({
                "category": self.category.code + " " + self.category.desc,
            })

        return geojson

    def __str__(self):
        return str(self.id) + " - " + str(self.area) + " га"


class ParametersMixin:
    """
        Additional parameters for main polygonal objects.
    """
    cadnum = Column(String(22), unique=True, nullable=False)

    @declared_attr
    def ownership_code(self):
        return Column(String(3), ForeignKey("ownership.code"), nullable=False)

    @declared_attr
    def ownership(self):
        return relationship("Ownership", backref=backref(self.__tablename__))

    @declared_attr
    def purpose_code(self):
        return Column(String(5), ForeignKey("purpose.code"), nullable=False)

    @declared_attr
    def purpose(self):
        return relationship("Purpose", backref=backref(self.__tablename__))

    def __str__(self):
        return self.cadnum


class CategoryMixin:
    """
        Additional parameters for all polygonal objects.
    """
    @declared_attr
    def category_code(self):
        return Column(String(3), ForeignKey("category.code"), nullable=False)

    @declared_attr
    def category(self):
        return relationship("Category", backref=backref(self.__tablename__))


#   Users --------------------------------------------------------------------------------------------------------------
class Users(Base, UserMixin):
    """
         The model is used for CRUD user data.
         Used for authenticate.
    """
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    tel = Column(String)

    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    active = Column(Boolean, nullable=False, default=True)
    fs_uniquifier = Column(String, unique=True, nullable=False)

    roles = relationship("Roles", secondary="usersroles", backref=backref(__name__.lower(), lazy="dynamic"))

    def __str__(self):
        return self.email


class Roles(Base, RoleMixin, CodeDescMixin):
    """
        The model defines roles for users.
    """
    name = Column(String, unique=True, nullable=False)


class UsersRoles(Base):
    """
        The model links users roles.
    """
    user_id = Column("user_id", Integer, ForeignKey("users.id"))
    role_id = Column("role_id", Integer, ForeignKey("roles.id"))


class History(Base):
    """
        The model is needed to track the history of site visits and search by users.
    """
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=lambda _: current_user.id)
    user_ip = Column(String(15), nullable=False, default=lambda _: request.headers.get('X-Real-IP'))
    message = Column(String(255))
    date = Column(DateTime, nullable=False, default=datetime.datetime.now)

    @declared_attr
    def user(self):
        return relationship("Users", backref=backref(self.__tablename__))


class Revision(Base):
    """
        Land plots revision date.
    """
    date = Column(Date, unique=True, nullable=False)

    def __str__(self):
        return self.date


#   ATU ----------------------------------------------------------------------------------------------------------------
class State(Base, GeometryMixin, CodeDescMixin):
    """
        Polygonal object.
        State of Ukraine.
    """
    pass


class District(Base, GeometryMixin, CodeDescMixin):
    """
        Polygonal object.
        Old districts of Ukrane.
    """
    pass


class Council(Base, GeometryMixin, CodeDescMixin):
    """
        Polygonal object.
        Old councils of Ukrane.
    """
    pass


class Village(Base, GeometryMixin, CodeDescMixin):
    """
        Polygonal object.
        Villages of Ukrane.
    """
    pass


#   Layers -------------------------------------------------------------------------------------------------------------
class Land(Base, GeometryMixin, CategoryMixin):
    """
        Polygonal object.
        Describes a plot of land without a cadastral number.
    """
    pass


class Cadastre(Base, GeometryMixin, ParametersMixin):
    """
        Main polygonal object.
        Describes a plot of lands with actual land cadastre data.
    """
    pass


class Archive(Base, GeometryMixin, ParametersMixin):
    """
        Main polygonal object.
        Describes a plot of lands with archive land cadastre data.
    """
    pass


#   Parameters ---------------------------------------------------------------------------------------------------------
class Ownership(Base, CodeDescMixin):
    """
        Additional parameter for main polygonal objects.
        Describes the form of land use ownership.
    """
    pass


class Category(Base, CodeDescMixin):
    """
        Additional parameter for all polygonal objects.
        Describes the category of land for the main purpose.
    """
    pass


class Purpose(Base, CodeDescMixin, CategoryMixin):
    """
        Additional parameter for main polygonal objects.
        Describes the intended purpose of the site within the main category of land.
    """
    pass


#   Event --------------------------------------------------------------------------------------------------------------
@event.listens_for(Users.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    """
        Hash the user's password if the password has changed.
    """
    if value != oldvalue:
        return hash_password(value)
    return value
