# backend/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Why create this file? To prevent circular imports.
# By initializing extensions here, we can safely import them
# into any part of our application (like models.py or app.py)
# without creating a dependency loop.

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()