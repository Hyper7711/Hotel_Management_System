from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from database.database import db, bcrypt, User, Room, Booking

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configuration for SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotel.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize db and bcrypt
db.init_app(app)
bcrypt.init_app(app)


# -----------------------------------------
# Home Page
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------------------
# Admin Login
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


# -----------------------------------------
# Admin Panel (Dashboard)
@app.route("/admin/panel")
def admin_panel():
    if not session.get("admin_logged_in"):
        flash("Please login as admin first.", "warning")
        return redirect(url_for("admin_login"))

    rooms = Room.query.all()

    # Handle bookings with try-except in case datetime fails
    bookings = []
    for booking in Booking.query.all():
        try:
            # This will ensure that datetime values are stringified properly
            booking.check_in_str = (
                booking.check_in.strftime("%Y-%m-%d %H:%M")
                if booking.check_in
                else "N/A"
            )
            booking.check_out_str = (
                booking.check_out.strftime("%Y-%m-%d %H:%M")
                if booking.check_out
                else "N/A"
            )
            bookings.append(booking)
        except Exception as e:
            print(f"Skipping booking ID {booking.id} due to error: {e}")
            continue

    return render_template("admin_panel.html", rooms=rooms, bookings=bookings)


# -----------------------------------------
# Add Room (Admin functionality)
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


# -----------------------------------------
# Admin Logout
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_email", None)
    flash("Admin logged out successfully.", "info")
    return redirect(url_for("admin_login"))


# -----------------------------------------
# Book Page (Visible to users)
@app.route("/book")
def book():
    rooms = Room.query.filter_by(availability=True).all()
    return render_template("book.html", rooms=rooms)


# -----------------------------------------
# Main
if __name__ == "__main__":
    app.run(debug=True)
