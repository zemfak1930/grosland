import datetime

from flask import request

from flask_security import UserMixin, RoleMixin, hash_password, current_user

from geoalchemy2 import Geometry

from grosland.dictionary import main_dictionary

from shapely.wkb import loads

from sqlalchemy import ForeignKey, Column, String, Integer, DECIMAL, Boolean, Date, DateTime, event
from sqlalchemy.orm import DeclarativeBase, relationship, backref, declared_attr


__all__ = ["Base", "Users", "Roles", "History", "Revision"] + \
          [_ + "View" for _ in value for key, value in main_dictionary.items()]


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
                    "coordinates": [
                        [[list(coord) for coord in polygon.exterior.coords]] +
                        [[list(coord) for coord in interior.coords] for interior in polygon.interiors]
                        for polygon in loads(bytes.fromhex(str(self.geometry))).geoms
                    ]
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


#   ATU / Layers / Parameters ------------------------------------------------------------------------------------------
for key, value in {
    "Atu": ("State", "District", "Council", "Village"),
    "Layers": ("Cadastre", "Archive", "Land"),
    "Parameters": ("Ownership", "Category", "Purpose"),
}.items():
    other_mixins = "CodeDescMixin, CategoryMixin"

    if key == "Atu":
        other_mixins = "GeometryMixin, CodeDescMixin"

    elif key == "Layers":
        other_mixins = "GeometryMixin, ParametersMixin"

    elif key == "Parameters":
        other_mixins = "CodeDescMixin"

    for _ in value:
        exec(f"class {_}(Base, {other_mixins}): pass")


#   Event --------------------------------------------------------------------------------------------------------------
@event.listens_for(Users.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    """
        Hash the user's password if the password has changed.
    """
    if value != oldvalue:
        return hash_password(value)
    return value
