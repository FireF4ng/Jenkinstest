from flask import render_template, redirect, url_for, session, request, jsonify
from model.user_model import Eleve, Professeur, Note, db
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

        # Check if user is a student
        user = Eleve.query.filter_by(username=username, mdp=password).first()
        if user:
            session["user"] = username
            session["role"] = "eleve"
            return redirect(url_for("main_controller.main_menu"))

        # Check if user is a professor
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
        return render_template("main.html", role=role, eleve=eleve, notes=notes)

    elif role == "professeur":
        professeur = Professeur.query.filter_by(username=session["user"]).first()

        if not professeur:
            return redirect(url_for("main_controller.logout"))

        # Get last graded students
        last_notes = (
            Note.query
            .join(Eleve)
            .join(Professeur, Professeur.id == Note.matiere_id)  # Assuming Prof is assigned to subjects
            .filter(Professeur.username == session["user"])
            .order_by(Note.date.desc())
            .limit(5)
            .all()
        )

        return render_template("main.html", role=role, professeur=professeur, last_notes=last_notes)

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
