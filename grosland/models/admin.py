from flask import redirect, url_for, request

from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import BaseForm

from flask_security import current_user

import uuid


__all__ = [
    "AdminView", "UsersView", "LandView", "CadastreView", "ArchiveView", "OwnershipView", "CategoryView", "PurposeView",
]


#   Base ---------------------------------------------------------------------------------------------------------------
class BaseUsersForm(BaseForm):
    def populate_obj(self, user):
        super().populate_obj(user)
        if user.fs_uniquifier is None:
            user.fs_uniquifier = uuid.uuid4().hex


#   Admin --------------------------------------------------------------------------------------------------------------
class AdminView(AdminIndexView):
    @staticmethod
    def is_accessible(**kwargs):
        return current_user.has_role("admin")

    @staticmethod
    def inaccessible_callback(name, **kwargs):
        return redirect(url_for("security.login", next=request.url))


#   Users --------------------------------------------------------------------------------------------------------------
class UsersView(ModelView):
    form_base_class = BaseUsersForm

    column_list = ("id", "active", "name", "surname", "email", "tel",)
    form_columns = ("active", "name", "surname", "email", "password", "tel", "roles",)


#   Layers -------------------------------------------------------------------------------------------------------------
class LandView(ModelView):
    column_list = ("id", "area", "category", "address",)
    form_columns = ("area", "category", "address")


class CadastreView(ModelView):
    column_list = ("id", "cadnum", "area", "ownership", "category", "purpose", "address",)
    form_columns = ("cadnum", "area", "ownership", "category", "purpose", "address",)


class ArchiveView(CadastreView):
    pass


#   Parameters ---------------------------------------------------------------------------------------------------------
class OwnershipView(ModelView):
    pass


class CategoryView(ModelView):
    pass


class PurposeView(ModelView):
    pass
