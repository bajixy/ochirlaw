import os
from flask import Flask
from .models import db


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    database_url = os.getenv("DATABASE_URL", "sqlite:///ochirlaw.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # connect database
    db.init_app(app)

    # register routes
    from .routes import main
    app.register_blueprint(main)

    # Create tables when app starts if they do not already exist.
    with app.app_context():
        print("Creating database tables if needed...")
        db.create_all()
        print("Database ready.")

    return app
