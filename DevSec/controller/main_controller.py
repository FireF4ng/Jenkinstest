from flask import render_template, redirect, url_for, session, request, jsonify
from model.user_model import Eleve, Professeur, Note, Classe, Matiere, ProfMatiere, db
from flask import Blueprint
import random

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

        user = Eleve.query.filter_by(username=username, mdp=password).first()
        if user:
            session["user"] = username
            session["role"] = "eleve"
            return redirect(url_for("main_controller.main_menu"))

        user = Professeur.query.filter_by(username=username, mdp=password).first()
        if user:
            session["user"] = username
            session["role"] = "professeur"
            return redirect(url_for("main_controller.main_menu"))

        message = "Erreur : Identifiant ou mot de passe incorrect"
    
    return render_template("login.html", message=message)

@main_controller.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("role", None)
    return redirect(url_for("main_controller.login"))

@main_controller.route("/main_menu")
def main_menu():
    if "user" not in session:
        return redirect(url_for("main_controller.login"))

    role = session.get("role")

    if role == "eleve":
        eleve = Eleve.query.filter_by(username=session["user"]).first()
        notes = eleve.get_notes() if eleve else []
        agenda = [
            {"matiere": m.matiere, "debut": f"{random.randint(8, 16)}H{random.choice(["00", "30"])}", "fin": f"{random.randint(8, 16)}H{random.choice(["00", "30"])}", "prof": (Professeur.query.filter_by(id=pm.professeur_id).first().nom +' '+ Professeur.query.filter_by(id=pm.professeur_id).first().prenom) if pm else "Inconnu"} 
            for pm in ProfMatiere.query.all() for m in Matiere.query.filter_by(id=pm.matiere_id).all()
        ]
        devoirs = [
            {"matiere": m.matiere, "contenu": "Exercice aléatoire"} for m in Matiere.query.all()
        ]
        return render_template("main.html", role=role, eleve=eleve, notes=notes, agenda=agenda, devoirs=devoirs)

    elif role == "professeur":
        professeur = Professeur.query.filter_by(username=session["user"]).first()
        if not professeur:
            return redirect(url_for("main_controller.logout"))

        last_notes = (
            Note.query
            .join(Eleve)
            .join(ProfMatiere, ProfMatiere.matiere_id == Note.matiere_id)
            .filter(ProfMatiere.professeur_id == professeur.id)
            .order_by(Note.date.desc())
            .limit(5)
            .all()
        )
        agenda = [
            {"classe": c.nom, "matiere": m.matiere, "debut": f"{random.randint(8, 16)}H{random.choice(["00", "30"])}", "fin": f"{random.randint(8, 16)}H{random.choice(["00", "30"])}"} 
            for c in Classe.query.all() for m in Matiere.query.all()
        ]
        devoirs = [
            {"classe": c.nom, "matiere": m.matiere, "contenu": "Devoir aléatoire"} 
            for c in Classe.query.all() for m in Matiere.query.all()
        ]
        return render_template("main.html", role=role, professeur=professeur, last_notes=last_notes, agenda=agenda, devoirs=devoirs)

    return redirect(url_for("main_controller.logout"))

@main_controller.route("/update_score", methods=["POST"])
def update_score():
    if "user" not in session or session.get("role") != "professeur":
        return jsonify({"error": "Unauthorized"}), 403

    note_id = request.form.get("note_id")
    new_score = request.form.get("new_score")

    note = Note.query.get(note_id)
    if note:
        note.note = new_score
        db.session.commit()
        return jsonify({"success": True, "new_score": new_score})

    return jsonify({"error": "Note not found"}), 404
