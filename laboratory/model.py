import click

from datetime import datetime

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask.cli import with_appcontext

from werkzeug.security import generate_password_hash, check_password_hash
from pytz import timezone, utc


db = SQLAlchemy()
migrate = Migrate()


def current_localtime(now, local_timezone=timezone('Asia/Seoul')):
    return utc.localize(now).astimezone(local_timezone)


class User(db.Model):
    __table_name__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    files = db.relationship('File', backref='uploader', lazy=True)

    def __init__(self, username, password, email, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User('{self.id}','{self.username}','{self.email}')>"


class FileType(db.Model):
    __table_name__ = "file_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    ext = db.Column(db.String(20))

    files = db.relationship('File', backref='type', lazy=True)

    def __init__(self, name, ext=None, description=None):
        self.name = name
        if ext is not None:
            self.ext = ext
        if description is not None:
            self.description = description

    def __repr__(self):
        return f"<FileType('{self.name}')>"


tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                db.Column('file_id', db.Integer, db.ForeignKey('file.id'), primary_key=True)
                )


class File(db.Model):
    __table_name__ = 'file'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), unique=True, nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    date_uploaded = db.Column(db.DateTime, default=current_localtime(datetime.utcnow()))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filetype_id = db.Column(db.Integer, db.ForeignKey('file_type.id'))
    tags = db.relationship(
        'Tag', secondary=tags, lazy='joined', backref=db.backref('files', lazy=True)
    )

    def __init__(self, filename, filepath, filetype=None, description=None):
        self.filename = filename
        self.filepath = filepath
        if filetype is not None:
            self.filetype = filetype
        if description is not None:
            self.description = description

    def __repr__(self):
        return f"<File('{self.filename}','{self.date_uploaded}')>"


class Tag(db.Model):
    __table_name__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)

    def __init__(self, name):
        name = self.name

    def __repr__(self):
        return f"<Tag('{self.name}')>"


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.init_app(app=current_app)
    db.drop_all()
    db.create_all()
    click.echo('Initialized the database.')
