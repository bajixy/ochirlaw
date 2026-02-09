import os
from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ochirlaw.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # connect database
    db.init_app(app)

    # register routes
    from .routes import main
    app.register_blueprint(main)

    # 🔥 FORCE DB CREATION WHEN APP STARTS
    with app.app_context():
        print("Creating database if not exists...")
        db.create_all()
        print("Database ready.")

    return app
