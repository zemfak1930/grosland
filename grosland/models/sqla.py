import datetime
from flask import request
from flask_security import UserMixin, RoleMixin, hash_password, current_user
from geoalchemy2 import Geometry
from shapely.wkb import loads
from sqlalchemy import ForeignKey, Column, String, Integer, DECIMAL, Boolean, DateTime, event
from sqlalchemy.orm import DeclarativeBase, relationship, backref, declared_attr


__all__ = [
    "Base",
    "Users", "Roles",
    "Ownership", "Category", "Purpose",
    "State", "District", "Council", "Village",
    "Cadastre", "Archive", "Land",
    "ASCM",
    "History", "Updates"
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


class MultipolygonMixin:
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
                    "address": self.address,
                    "cadnum": self.cadnum,
                    "ownership": self.ownership_code + " " + self.ownership.desc + " власність",
                    "purpose": self.purpose_code + " " + self.purpose.desc
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

        return geojson

    def __str__(self):
        return str(self.id) + " - " + str(self.area) + " га"


class PointMixin:
    """
        Base parameters for all points objects.
    """
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    color = Column(String(10), nullable=False)

    def __str__(self):
        return str(self.id)


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


#   Parameters  --------------------------------------------------------------------------------------------------------
class Ownership(Base, CodeDescMixin):
    """
        Forms of lot ownership.
    """
    pass


class Category(Base, CodeDescMixin):
    """
        Category of land lots.
    """
    pass


class Purpose(Base, CodeDescMixin):
    """
        Lot use designation.
    """
    pass


#   ATU ----------------------------------------------------------------------------------------------------------------
class State(Base, MultipolygonMixin, CodeDescMixin):
    """
        States of Ukraine.
    """
    pass


class District(Base, MultipolygonMixin, CodeDescMixin):
    """
        Districts of Ukraine.
    """
    pass


class Council(Base, MultipolygonMixin, CodeDescMixin):
    """
        Councils of Ukraine.
    """
    pass


class Village(Base, MultipolygonMixin, CodeDescMixin):
    """
        Villages of Ukraine.
    """
    pass


#   Lots    ------------------------------------------------------------------------------------------------------------
class Cadastre(Base, MultipolygonMixin, ParametersMixin):
    """
        The current cadastral information.
    """
    pass


class Archive(Base, MultipolygonMixin, ParametersMixin):
    """
        The archive cadastral information.
    """
    pass


class Land(Base, MultipolygonMixin, ParametersMixin):
    """
        User's custom polygons.
    """
    pass


#   Points  ------------------------------------------------------------------------------------------------------------
class ASCM(Base, CodeDescMixin, PointMixin):
    """
        Alberta Survey Control Marker.
    """
    pass


#   Auxiliary classes   ------------------------------------------------------------------------------------------------
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
        return relationship("Users", backref=backref(self.__tablename__, lazy="dynamic"))


class Updates(Base):
    """
        Model for storing data about the latest updates on the site.
    """
    title = Column(String(100), nullable=False)
    content = Column(String(600), nullable=False)
    image_url = Column(String(100))
    date = Column(DateTime, default=datetime.datetime.now, nullable=False)

    def __str__(self):
        return self.title


#   Event --------------------------------------------------------------------------------------------------------------
@event.listens_for(Users.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    """
        Hash the user's password if the password has changed.
    """
    if value != oldvalue:
        return hash_password(value)
    return value
