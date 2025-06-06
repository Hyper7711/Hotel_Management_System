from flask import Flask
from flask_migrate import Migrate
from .database import db, bcrypt, User, Room, Booking

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotel.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)  # Yeh line add kar

    # Register Blueprints if any

    return app
