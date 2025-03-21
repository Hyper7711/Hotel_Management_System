import os
from flask import Flask, render_template
from database.database import db
from flask_migrate import Migrate
from routes import register_routes

app = Flask(__name__)

# Get absolute path of the directory where app.py is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Set database path dynamically
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "instance", "hotel.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"  # Needed for session management

# Initialize database
db.init_app(app)

# Initialize Migrate for database migrations
migrate = Migrate(app, db)

# Register routes
register_routes(app)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    # Ensure tables are created within the app context
    with app.app_context():
        db.create_all()
    app.run(debug=True)
