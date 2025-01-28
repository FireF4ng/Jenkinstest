from flask import render_template, redirect, url_for, session, request
from model.user_model import User, db
from flask import Blueprint

main_controller = Blueprint("main_controller", __name__)

@main_controller.route("/")
def home():
    if "user" in session:
        return redirect(url_for("main_controller.main_menu"))
    return redirect(url_for("main_controller.login"))

@main_controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user"] = user.username
            return redirect(url_for("main_controller.main_menu"))
    return render_template("login.html")

@main_controller.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("main_controller.login"))

@main_controller.route("/main_menu")
def main_menu():
    if "user" not in session:
        return redirect(url_for("main_controller.login"))
    return render_template("main_menu.html")
