from flask import render_template, request, redirect, url_for, flash, session
from database.database import db, User, Room, Booking
from datetime import datetime


def register_routes(app):
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")

            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered!", "danger")
                return redirect(url_for("register"))

            # Create new user
            new_user = User(name=name, email=email)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                session["user_id"] = user.id
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid email or password!", "danger")

        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            flash("Please log in first!", "warning")
            return redirect(url_for("login"))
        return "Welcome to your dashboard!"

    @app.route("/logout")
    def logout():
        session.pop("user_id", None)
        flash("Logged out successfully!", "info")
        return redirect(url_for("login"))

    # ✅ Book a Room
    @app.route("/book", methods=["GET", "POST"])
    def book():
        if request.method == "POST":
            customer_name = request.form.get("customer_name")
            room_id = request.form.get("room_id")
            check_in = request.form.get("check_in")
            check_out = request.form.get("check_out")

            if "user_id" not in session:
                flash("Please log in to book a room!", "warning")
                return redirect(url_for("login"))

            # Convert string dates to datetime
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")

            new_booking = Booking(
                customer_name=customer_name,
                room_id=room_id,
                check_in=check_in_date,
                check_out=check_out_date,
            )

            db.session.add(new_booking)
            db.session.commit()

            flash("Room booked successfully!", "success")
            return redirect(url_for("dashboard"))

        rooms = Room.query.filter_by(availability=True).all()
        return render_template("book.html", rooms=rooms)

    # ✅ Admin Dashboard
    @app.route("/admin")
    def admin_dashboard():
        rooms = Room.query.all()
        bookings = Booking.query.all()
        return render_template("admin.html", rooms=rooms, bookings=bookings)
