import os

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .model import (
    db, migrate, User, File, FileType, Tag, init_db_command
)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    admin = Admin(app, template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(FileType, db.session))
    admin.add_view(ModelView(File, db.session))
    admin.add_view(ModelView(Tag, db.session))

    app.cli.add_command(init_db_command)
    db.init_app(app)
    migrate.init_app(app, db)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import storage
    app.register_blueprint(storage.bp)

    app.add_url_rule('/', endpoint='index')

    return app
