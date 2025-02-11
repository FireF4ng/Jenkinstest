from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask_wtf.csrf import generate_csrf
from model.user_model import Eleve, Professeur
import time

auth_controller = Blueprint("auth_controller", __name__)

auth_controller = Blueprint("auth_controller", __name__)
LOGIN_ROUTE = "auth_controller.login"

@auth_controller.route("/")
def home():
    if "user" in session:
        return redirect(url_for("auth_controller.main_menu"))
    return redirect(url_for(LOGIN_ROUTE))

@auth_controller.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    message = "Veuillez entrer votre identifiant et mot de passe"
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return jsonify({"error": "Champs obligatoires manquants"}), 400

        user = Eleve.query.filter_by(username=username).first() or Professeur.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session["user"] = user.id
            session["role"] = "eleve" if isinstance(user, Eleve) else "professeur"
            return redirect(url_for("auth_controller.main_menu"))
        
        message = "Identifiants incorrects"
        time.sleep(2)  # Prevents brute-force attacks
    
    return render_template("login.html", message=message, csrf_token=generate_csrf())

@auth_controller.route("/logout")
def logout():
    """Logs out the user and clears session."""
    session.pop("user", None)
    session.pop("role", None)
    return redirect(url_for(LOGIN_ROUTE))

@auth_controller.route("/main_menu")
def main_menu():
    """Redirects users based on their role (student or professor)."""
    if "user" not in session:
        return redirect(url_for(LOGIN_ROUTE))
    
    if session["user"] == 0:
        return redirect(url_for("admin_controller.admin_dashboard"))
    elif session["role"] == "eleve":
        return redirect(url_for("general_controller.student_dashboard"))
    elif session["role"] == "professeur":
        return redirect(url_for("general_controller.teacher_dashboard"))
    
    return redirect(url_for("auth_controller.logout"))  # Fallback
