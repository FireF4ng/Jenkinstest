from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask_wtf.csrf import generate_csrf
from model.user_model import Eleve, Professeur
from extensions import limiter, logger
import time
import re

auth_controller = Blueprint("auth_controller", __name__)

LOGIN_ROUTE = "auth_controller.login"
MAIN_MENU_ROUTE = "auth_controller.main_menu"

def is_valid_username(username, password):
    """Empêche l'injection SQL en vérifiant les caractères autorisés"""
    return bool(re.match(r"^[a-zA-Z0-9_]+$", password)) and bool(re.match(r"^[a-zA-Z0-9_]+$", username))

@auth_controller.route("/")
def home():
    if "user" in session:
        return redirect(url_for(MAIN_MENU_ROUTE))
    return redirect(url_for(LOGIN_ROUTE))

@auth_controller.route("/login", methods=["GET"])
def login_form():
    """Affiche le formulaire de connexion."""
    if "user" in session:
        return redirect(url_for(MAIN_MENU_ROUTE))
    return render_template("login.html", csrf_token=generate_csrf())

@auth_controller.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """Traite la soumission du formulaire de connexion."""
    if "user" in session:
        return redirect(url_for(MAIN_MENU_ROUTE))

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not is_valid_username(username, password):
        logger.warning(f"Tentative de connexion suspecte - Username invalide : {username}")
        time.sleep(0.5)
        return render_template("login.html", message="Nom d'utilisateur invalide", csrf_token=generate_csrf())

    user = Eleve.query.filter_by(username=username).first() or Professeur.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session["user"] = user.id
        session["role"] = "eleve" if isinstance(user, Eleve) else "professeur"
        return redirect(url_for(MAIN_MENU_ROUTE))

    logger.warning(f"Tentative de connexion echouee pour l'utilisateur : {username}")

    return render_template("login.html", message="Identifiants incorrects", csrf_token=generate_csrf())

@auth_controller.route("/logout")
def logout():
    """Logs out the user and clears session."""
    session.clear()
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
