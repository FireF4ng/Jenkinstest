from flask import render_template, redirect, url_for, session, request
from model.user_model import Eleve, Note, db
from flask import Blueprint

main_controller = Blueprint("main_controller", __name__)

@main_controller.route("/")
def home():
    if "user" in session:
        return redirect(url_for("main_controller.main_menu"))
    return redirect(url_for("main_controller.login"))

@main_controller.route("/login", methods=["GET", "POST"])
def login():
    message = 'Veuillez entrer votre identifiant et mot de passe'
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        eleve = Eleve.query.filter_by(username=username, mdp=password).first()
        
        if not eleve:
            message = "Erreur : Identifiant ou mot de passe incorrect"
        else:
            session["user"] = eleve.username
            return redirect(url_for("main_controller.main_menu"))
    
    return render_template("login.html", message=message)

@main_controller.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("main_controller.login"))

@main_controller.route("/main_menu")
def main_menu():
    if "user" not in session:
        return redirect(url_for("main_controller.login"))

    eleve = Eleve.query.filter_by(username=session["user"]).first()
    notes = eleve.get_notes() if eleve else []

    return render_template("main.html", eleve=eleve, notes=notes)