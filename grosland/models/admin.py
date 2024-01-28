from flask import redirect, url_for, request

from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import BaseForm

from flask_security import current_user

import uuid


__all__ = [
    "AdminView", "UsersView", "HistoryView", "RevisionView", "LandView", "CadastreView", "ArchiveView", "OwnershipView",
    "CategoryView", "PurposeView",
]


#   Base ---------------------------------------------------------------------------------------------------------------
class BaseUsersForm(BaseForm):
    """
        Automatic generation of basic user parameters.
    """
    def populate_obj(self, user):
        super().populate_obj(user)
        if user.fs_uniquifier is None:
            user.fs_uniquifier = uuid.uuid4().hex


#   Admin --------------------------------------------------------------------------------------------------------------
class AdminView(AdminIndexView):
    """
        Displaying the admin control panel.
    """
    @staticmethod
    def is_accessible(**kwargs):
        return current_user.has_role("admin")

    @staticmethod
    def inaccessible_callback(name, **kwargs):
        return redirect(url_for("security.login", next=request.url))


#   Users --------------------------------------------------------------------------------------------------------------
class UsersView(ModelView):
    """
        Manipulating the user model.
    """
    form_base_class = BaseUsersForm

    column_list = ("id", "active", "name", "surname", "email", "tel",)
    form_columns = ("active", "name", "surname", "email", "password", "tel", "roles",)


class HistoryView(ModelView):
    """
        Displaying user login and search history.
    """
    can_create = False
    can_edit = False

    column_default_sort = ("date", True,)
    column_list = ("user.surname", "user", "message", "user_ip", "date",)
    column_searchable_list = ("message",)


class RevisionView(ModelView):
    """
        Displaying land plot revision date.
    """
    pass


#   Layers -------------------------------------------------------------------------------------------------------------
class LandView(ModelView):
    """
        Managing a model of a land plot without a cadastral number.
    """
    column_list = ("id", "area", "category", "address",)
    form_columns = ("area", "category", "address")


class CadastreView(ModelView):
    """
        Managing a model of a land plot with actual land cadastre data.
    """
    column_list = ("id", "cadnum", "area", "ownership", "purpose.category", "purpose", "address",)
    form_columns = ("cadnum", "area", "ownership", "purpose", "address",)


class ArchiveView(CadastreView):
    """
        Managing a model of a land plot with archive land cadastre data.
    """
    pass


#   Parameters ---------------------------------------------------------------------------------------------------------
class OwnershipView(ModelView):
    """
        Managing a model of form of land use ownership.
    """
    pass


class CategoryView(ModelView):
    """
        Managing a model of category of land for the main purpose.
    """
    pass


class PurposeView(ModelView):
    """
        Managing a model of intended purpose of the site within the main category of land.
    """
    pass
