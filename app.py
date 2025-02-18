from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/hotel.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_secret_key"  # Change this to a strong secret key

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)


# Define Room Model
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)


# Create database tables
with app.app_context():
    db.create_all()


# Home route
@app.route("/")
def home():
    return render_template("index.html")


# User Registration
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Check if all fields are provided
    if (
        not data.get("name")
        or not data.get("email")
        or not data.get("password")
        or not data.get("role")
    ):
        return jsonify({"message": "Missing fields"}), 400

    # Check if user already exists
    user = User.query.filter_by(email=data["email"]).first()
    if user:
        return jsonify({"message": "User already exists"}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    # Create the user object
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password,
        role=data["role"],
    )

    # Save to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201


# User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    # Check if email and password are provided
    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing email or password"}), 400

    # Check if the user exists
    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check if the password matches
    if not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid password"}), 401

    # Create a JWT token
    access_token = create_access_token(identity=user.id)

    return jsonify({"message": "Login successful!", "access_token": access_token}), 200


# Protected route: User profile
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    # Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    return (
        jsonify(
            {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
        ),
        200,
    )


# Room Booking (for authenticated users)
@app.route("/book-room", methods=["POST"])
@jwt_required()
def book_room():
    data = request.get_json()

    # Check if room ID is provided
    if not data.get("room_id"):
        return jsonify({"message": "Missing room ID"}), 400

    # Check if room exists and is available
    room = Room.query.get(data["room_id"])
    if not room:
        return jsonify({"message": "Room not found"}), 404
    if not room.available:
        return jsonify({"message": "Room not available"}), 400

    # Mark room as booked
    room.available = False
    db.session.commit()

    return jsonify({"message": "Room booked successfully!"}), 200


if __name__ == "__main__":
    app.run(debug=True)
