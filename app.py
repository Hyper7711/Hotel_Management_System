import os
from flask import Flask, render_template
from database.database import db, Room, Booking

app = Flask(__name__)

# Get absolute path of the directory where app.py is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Set database path dynamically
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "instance", "hotel.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don’t exist
    app.run(debug=True)
