# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate, jwt # Import from extensions.py
import click

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt.init_app(app)
    
    # Import and register models
    from . import models
    # Import and register blueprints
    from .routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    # A simple test route
    @app.route('/')
    def index():
        return jsonify({'message': 'Welcome to the Quiz Master API!'})
    
    @app.cli.command("create-admin")
    def create_admin():
        """Creates the initial admin user."""
        from .models import User
        # Check if an admin user already exists
        if User.query.filter_by(is_admin=True).first():
            print("Admin user already exists.")
            return

        admin_user = User(
            username="admin@quizmaster.com",
            full_name="Quiz Master Admin",
            is_admin=True
        )
        # IMPORTANT: Use a secure password in a real application!
        admin_user.set_password("AdminPassword123")
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully.")

    @app.cli.command("reset-admin-password")
    @click.argument("new_password")
    def reset_admin_password(new_password):
        """Resets the admin user's password."""
        from .models import User
        
        # Why use @click.argument? It allows us to pass a value
        # (the new password) directly on the command line.

        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            admin_user.set_password(new_password)
            db.session.commit()
            print("Admin password has been reset successfully.")
        else:
            print("Admin user not found.")
            
    return app

    