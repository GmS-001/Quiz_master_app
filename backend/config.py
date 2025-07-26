import os
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv() # This line explicitly finds and loads the .env file
basedir = os.path.abspath(os.path.dirname(__file__)) # Gets the absolute path of the directory where this file is located.

class Config:
    """Set Flask configuration variables."""
    # Specifies the database URI. It will create a file named 'app.db'
    # inside the 'backend' directory.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-key-change-it-later' # Change this key later!
    # Celery Configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_BEAT_SCHEDULE = {
        'send-daily-reminders': {
            'task': 'backend.celery_worker.send_daily_reminders',
            'schedule': crontab(hour=19, minute=0),
        },
    }
    # Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')