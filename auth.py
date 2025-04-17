from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from database.database import db, User

# Create a single blueprint with a consistent prefix
auth = Blueprint("auth", __name__, url_prefix="/auth")


# ------------------ Register Route ------------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        username = request.form.get("username") or request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("⚠️ Email already registered!", "warning")
            return redirect(url_for("auth.register"))

        # Create new user
        new_user = User(username=username, email=email, role="user")
        new_user.set_password(password)

        # Save to database
        db.session.add(new_user)
        db.session.commit()

        flash("✅ Registered successfully! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ------------------ Login Route ------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get form data
        email = request.form.get("email")
        password = request.form.get("password")

        # Authenticate user
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Set up both session and flask-login
            login_user(user)
            session["user_id"] = user.id
            session["user_logged_in"] = True
            session["user_name"] = user.username

            flash("✅ Login successful!", "success")
            # Redirect to main booking page
            return redirect(url_for("book_room"))
        else:
            flash("❌ Invalid email or password!", "danger")

    return render_template("login.html")


# ------------------ Dashboard Route ------------------
@auth.route("/dashboard")
@login_required
def dashboard():
    """User dashboard accessible only to logged-in users."""
    return render_template("dashboard.html", username=current_user.username)


# ------------------ Logout Route ------------------
@auth.route("/logout")
@login_required
def logout():
    # Properly log out with flask-login
    logout_user()
    # Also clear session data
    session.clear()

    flash("👋 Logged out successfully!", "info")
    return redirect(url_for("auth.login"))
