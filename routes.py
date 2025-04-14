from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.database import db, User, Room, Booking
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key


# ✅ Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("book"))  # ✅ redirect to book page
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")


# ✅ Dashboard Route
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))
    return "Welcome to your dashboard!"


# ✅ Logout Route
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))


# ✅ Book a Room Route
@app.route("/book_rook", methods=["GET", "POST"])
def book():
    if "user_id" not in session:
        flash("Please log in to book a room!", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        room_id = request.form.get("room_id")
        check_in = request.form.get("check_in")
        check_out = request.form.get("check_out")

        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")

        new_booking = Booking(
            customer_name=customer_name,
            room_id=room_id,
            check_in=check_in_date,
            check_out=check_out_date,
        )

        db.session.add(new_booking)

        # Set room availability to False
        room = Room.query.get(room_id)
        if room:
            room.availability = False

        db.session.commit()

        flash("Room booked successfully!", "success")
        return redirect(url_for("dashboard"))

    rooms = Room.query.filter_by(availability=True).all()
    return render_template("book.html", rooms=rooms)


# ✅ Admin Dashboard Route
@app.route("/admin")
def admin_dashboard():
    rooms = Room.query.all()
    bookings = Booking.query.all()
    return render_template("admin.html", rooms=rooms, bookings=bookings)


# ✅ Run App
if __name__ == "__main__":
    app.run(debug=True)
