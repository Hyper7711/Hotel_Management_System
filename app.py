from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from sqlalchemy import func
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from database import db, bcrypt
from database.database import User, Room, Booking
from auth import auth

# -----------------------------------------
# App Initialization
app = Flask(__name__)
app.secret_key = "supersecretkey"

# ------------------------------------------
# Register user blueprints
app.register_blueprint(auth)

# -----------------------------------------
# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotel.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# -----------------------------------------
# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

# -----------------------------------------
# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # Use your auth blueprint's login route

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------------------------
# Routes

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    customer_name = request.form['customer_name']
    room_type = request.form['room_type']
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    phone = request.form['phone']
    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']

    # Simple confirm page without SMS
    return render_template('confirmation.html',
                            customer_name=customer_name,
                            room_type=room_type,
                            check_in=check_in,
                            check_out=check_out,
                            phone=phone
                        )


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, role="admin").first()

        if user and user.check_password(password):
            session["admin_logged_in"] = True
            session["admin_email"] = email
            flash("Login successful!", "success")
            return redirect(url_for("admin_panel"))
        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

@app.route("/admin/panel")
def admin_panel():
    if not session.get("admin_logged_in"):
        flash("Please login as admin first.", "warning")
        return redirect(url_for("admin_login"))

    rooms = Room.query.all()
    bookings = []

    for booking in Booking.query.all():
        try:
            booking.check_in_str = booking.check_in.strftime("%Y-%m-%d %H:%M") if booking.check_in else "N/A"
            booking.check_out_str = booking.check_out.strftime("%Y-%m-%d %H:%M") if booking.check_out else "N/A"
            bookings.append(booking)
        except Exception as e:
            print(f"Skipping booking ID {booking.id} due to error: {e}")
            continue

    return render_template("admin_panel.html", rooms=rooms, bookings=bookings)

@app.route("/admin/add_room", methods=["POST"])
def add_room():
    if not session.get("admin_logged_in"):
        flash("Unauthorized access!", "danger")
        return redirect(url_for("admin_login"))

    room_number = request.form["room_number"]
    room_type = request.form["room_type"]
    price = request.form["price"]
    availability = bool(int(request.form["availability"]))

    new_room = Room(
        room_number=room_number,
        room_type=room_type,
        price=price,
        availability=availability,
    )

    db.session.add(new_room)
    db.session.commit()
    flash("Room added successfully!", "success")
    return redirect(url_for("admin_panel"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_email", None)
    flash("Admin logged out successfully.", "info")
    return redirect(url_for("admin_login"))

@app.route("/book")
def book():
    room_groups = (
        db.session.query(
            Room.room_type,
            db.func.min(Room.price).label("min_price"),
            db.func.max(Room.price).label("max_price"),
        )
        .group_by(Room.room_type)
        .all()
    )

    return render_template("book.html", room_groups=room_groups)

@app.route("/book_room", methods=["POST"])
def book_room():
    customer_name = request.form["customer_name"]
    room_type = request.form["room_type"]
    check_in = datetime.strptime(request.form["check_in"], "%Y-%m-%dT%H:%M")
    check_out = datetime.strptime(request.form["check_out"], "%Y-%m-%dT%H:%M")

    room = Room.query.filter_by(room_type=room_type, availability=True).first()

    if not room:
        flash("No available room for selected type.", "danger")
        return redirect(url_for("book"))

    new_booking = Booking(
        customer_name=customer_name,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
    )

    room.availability = False
    db.session.add(new_booking)
    db.session.commit()

    flash(f"{room.room_type} Room booked successfully!", "success")
    return redirect(url_for("index"))

@app.route("/payment", methods=["POST"])
def payment():
    customer_name = request.form["customer_name"]
    room_type = request.form["room_type"]
    check_in = request.form["check_in"]
    check_out = request.form["check_out"]

    return render_template("payment.html", customer_name=customer_name, room_type=room_type, check_in=check_in, check_out=check_out)


# -----------------------------------------
# Main
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Create default admin
        admin_email = "admin@hotel.com"
        if not User.query.filter_by(email=admin_email).first():
            admin_user = User(username="Admin", email=admin_email, role="admin")
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            print("[+] Admin user created")

        # Add sample rooms if empty
        if Room.query.count() == 0:
            sample_rooms = [
                Room(room_number="BUD-101", room_type="Budget", price=1000, availability=True),
                Room(room_number="DEL-201", room_type="Deluxe", price=2500, availability=True),
                Room(room_number="EXE-301", room_type="Executive", price=3500, availability=True),
                Room(room_number="STD-401", room_type="Standard", price=2000, availability=True),
                Room(room_number="SUI-501", room_type="Suite", price=6000, availability=True),
]

            db.session.bulk_save_objects(sample_rooms)
            print("[+] Sample rooms added")

        db.session.commit()

    app.run(debug=True)
