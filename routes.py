from flask import render_template, request, redirect, url_for, flash, session
from database.database import db, User


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

            # Create a new user
            new_user = User(name=name, email=email)
            new_user.set_password(password)  # Hash password before storing

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
                session["user_id"] = user.id  # Store user in session
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))  # Redirect to dashboard
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
