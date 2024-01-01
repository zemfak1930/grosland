from flask_security import UserMixin, RoleMixin, hash_password

from sqlalchemy import ForeignKey, Column, String, Integer, DECIMAL, Boolean, event
from sqlalchemy.orm import DeclarativeBase, relationship, backref, declared_attr

from geoalchemy2 import Geometry


__all__ = [
    "Base", "Users", "Roles", "Land", "Cadastre", "Archive", "Ownership", "Category", "Purpose"
]


#   Base ---------------------------------------------------------------------------------------------------------------
class Base(DeclarativeBase):
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


#   Mixin --------------------------------------------------------------------------------------------------------------
class CodeDescMixin:
    code = Column(String, unique=True, nullable=False)
    desc = Column(String, nullable=False)

    def __str__(self):
        return self.desc


class GeometryMixin:
    area = Column(DECIMAL(8, 4), nullable=False)
    address = Column(String(255))
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)


class ParametersMixin:
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
    @declared_attr
    def category_code(self):
        return Column(String(3), ForeignKey("category.code"), nullable=False)

    @declared_attr
    def category(self):
        return relationship("Category", backref=backref(self.__tablename__))


#   Users --------------------------------------------------------------------------------------------------------------
class Users(Base, UserMixin):
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
    name = Column(String, unique=True, nullable=False)


class UsersRoles(Base):
    user_id = Column("user_id", Integer, ForeignKey("users.id"))
    role_id = Column("role_id", Integer, ForeignKey("roles.id"))


#   Layers -------------------------------------------------------------------------------------------------------------
class Land(Base, GeometryMixin, CategoryMixin):
    def __str__(self):
        return self.id + " - " + self.area + " га"


class Cadastre(Base, GeometryMixin, ParametersMixin):
    pass


class Archive(Base, GeometryMixin, ParametersMixin):
    pass


#   Parameters ---------------------------------------------------------------------------------------------------------
class Ownership(Base, CodeDescMixin):
    pass


class Category(Base, CodeDescMixin):
    pass


class Purpose(Base, CodeDescMixin, CategoryMixin):
    pass


#   Event --------------------------------------------------------------------------------------------------------------
@event.listens_for(Users.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return hash_password(value)
    return value
