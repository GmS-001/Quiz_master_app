import os

# Gets the absolute path of the directory where this file is located.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Set Flask configuration variables."""
    # Specifies the database URI. It will create a file named 'app.db'
    # inside the 'backend' directory.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-key-change-it-later' # Change this key later!