from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db, bcrypt, User

auth = Blueprint("auth", __name__, url_prefix="/user")


# -----------------------------------------
# Register
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Username already taken!", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(username=username, email=email, role="user")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# -----------------------------------------
# Login
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("book"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")


# -----------------------------------------
# Dashboard (optional)
@auth.route("/dashboard")
def dashboard():
    if not session.get("user_logged_in"):
        flash("Please login to access dashboard", "warning")
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html", username=session.get("user_name"))


# -----------------------------------------
# Logout
@auth.route("/logout")
def logout():
    session.pop("user_logged_in", None)
    session.pop("user_name", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
