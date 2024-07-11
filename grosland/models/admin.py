from flask import redirect, url_for, request

from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import BaseForm

from flask_security import current_user

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from grosland.dictionary import main_dictionary

from markupsafe import Markup

import os

import uuid

from wtforms import StringField, TextAreaField, DateTimeLocalField
from wtforms.validators import DataRequired


__all__ = ["AdminView", "UsersView", "HistoryView", "RevisionView", "UpdatesView"]

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


class UpdatesForm(FlaskForm):
    """
        Base form for class UpdatesView.
    """
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    date = DateTimeLocalField('DateTime', format='%Y-%m-%d', validators=[DataRequired()])


class UpdatesView(ModelView):
    """
        Displaying website updates.
    """
    form = UpdatesForm

    column_formatters = {
        'image_url': lambda v, c, m, p:
        Markup(f'<div style="display: flex; justify-content: center;">'
               f'<img src="{os.path.join("/static/uploads", m.image_url)}" '
               f'style="max-width:150px; max-height:150px;"></div>')
        if m.image_url else None
    }

    def __init__(self, model, session, **kwargs):
        super(UpdatesView, self).__init__(model, session, **kwargs)
        self.upload_path = os.path.join('grosland', 'static', 'uploads')

    @staticmethod
    def random_filename(filename):
        return ''.join(uuid.uuid4().hex) + '.' + filename.rsplit('.', 1)[1]

    def on_model_change(self, form, model, is_created):
        if form.image.data:
            # Generate a random filename
            filename = self.random_filename(form.image.data.filename)
            filepath = os.path.join(self.upload_path, filename)

            # Remove old file if it exists
            if model.image_url:
                try:
                    old_file_path = os.path.join(self.upload_path, model.image_url)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                except Exception as e:
                    print(f"Failed to remove old file: {e}")

            # Save the new file
            form.image.data.save(filepath)
            model.image_url = os.path.relpath(filepath, self.upload_path)

    def on_model_delete(self, model):
        if model.image_url:
            try:
                file_path = os.path.join(self.upload_path, model.image_url)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to remove file: {e}")


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
