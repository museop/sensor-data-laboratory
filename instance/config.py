import os


base_dir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'THIS IS SECRET'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'storage.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOAD_FOLDER = os.path.join(base_dir, '../upload')
