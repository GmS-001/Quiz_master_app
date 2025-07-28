# backend/extensions.py
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import redis

# Why create this file? To prevent circular imports.
# By initializing extensions here, we can safely import them
# into any part of our application (like models.py or app.py)
# without creating a dependency loop.

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
# decode_responses=True ensures we get strings back from Redis, not bytes
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)