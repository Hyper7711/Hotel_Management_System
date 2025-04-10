from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from database import db, User

auth = Blueprint("auth", __name__)


# ------------------ Register Route ------------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("⚠️ Email already registered!", "warning")
            return redirect(url_for("auth.register"))

        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("✅ Registered successfully! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ------------------ Login Route ------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("✅ Logged in successfully!", "success")
            return redirect(url_for("dashboard"))

        flash("❌ Invalid credentials!", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


# ------------------ Logout Route ------------------
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("👋 Logged out successfully!", "info")
    return redirect(url_for("auth.login"))
