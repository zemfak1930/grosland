from flask import redirect, url_for, request

from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import BaseForm

from flask_security import current_user

from grosland.dictionary import main_dictionary

import uuid


__all__ = ["AdminView", "UsersView", "HistoryView", "RevisionView"]

for key, value in main_dictionary.items():
    __all__.extend([_ + "View" for _ in value])


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


#   ATU / Layers / Parameters ------------------------------------------------------------------------------------------
for key, value in main_dictionary.items():
    attributes = """
        column_list = ("id", "cadnum", "area", "ownership", "purpose", "address",)\n
        form_columns = ("cadnum", "area", "ownership", "purpose", "address",)\n
        column_searchable_list = ("cadnum",)
    """

    for _ in value:
        exec(f"class {_}View(ModelView):\n\t"
             f"{attributes if key == 'Layers' else 'pass'}")
