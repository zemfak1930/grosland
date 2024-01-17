import datetime

from flask import request

from flask_security import UserMixin, RoleMixin, hash_password, current_user

from geoalchemy2 import Geometry

from sqlalchemy import ForeignKey, Column, String, Integer, DECIMAL, Boolean, DateTime, event
from sqlalchemy.orm import DeclarativeBase, relationship, backref, declared_attr


__all__ = [
    "Base", "Users", "Roles", "History", "Land", "Cadastre", "Archive", "Ownership", "Category", "Purpose"
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
    area = Column(DECIMAL(8, 4), nullable=False)
    address = Column(String(255))
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)


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
    user_ip = Column(String(15), nullable=False, default=lambda _: request.remote_addr)
    cadnum = Column(String(22))
    date = Column(DateTime, nullable=False, default=datetime.datetime.now)

    @declared_attr
    def user(self):
        return relationship("Users", backref=backref(self.__tablename__))


#   Layers -------------------------------------------------------------------------------------------------------------
class Land(Base, GeometryMixin, CategoryMixin):
    """
        Polygonal object.
        Describes a plot of land without a cadastral number.
    """
    def __str__(self):
        return self.id + " - " + self.area + " га"


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
