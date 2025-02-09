from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from model.user_model import Eleve, Professeur, Classe, Note, Matiere, ProfMatiere
from model.user_model import db
import random

general_controller = Blueprint("general_controller", __name__)


@general_controller.route("/student_dashboard")
def student_dashboard():
    """Loads student main menu with agenda and homework."""
    if "user" not in session or session["role"] != "eleve":
        return redirect(url_for("auth_controller.login"))

    role = session.get("role")
    eleve = Eleve.query.filter_by(id=session["user"]).first()
    notes = eleve.get_notes() if eleve else []
    agenda = [
        {"matiere": m.matiere, "debut": f"{random.randint(8, 16)}H{random.choice(["00", "30"])}", "fin": f"{random.randint(8, 16)}H{random.choice(["00", "30"])}", "prof": (Professeur.query.filter_by(id=pm.professeur_id).first().nom +' '+ Professeur.query.filter_by(id=pm.professeur_id).first().prenom) if pm else "Inconnu"} 
        for pm in ProfMatiere.query.all() for m in Matiere.query.filter_by(id=pm.matiere_id).all()
    ]
    devoirs = [
        {"matiere": m.matiere, "contenu": "Exercice aléatoire"} for m in Matiere.query.all()
    ]
    return render_template("main.html", role=role, eleve=eleve, notes=notes, agenda=agenda, devoirs=devoirs)


@general_controller.route("/teacher_dashboard")
def teacher_dashboard():
    """Loads teacher dashboard with recent student grades."""
    if "user" not in session or session["role"] != "professeur":
        return redirect(url_for("auth_controller.login"))

    professeur = Professeur.query.filter_by(id=session["user"]).first()
    role = session.get("role")

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


@general_controller.route("/update_score", methods=["POST"])
def update_score():
    if "user" not in session or session.get("role") != "professeur":
        return jsonify({"error": "Unauthorized"}), 403

    note_id = request.form.get("note_id")
    new_score = request.form.get("new_score")
    if not 0 < int(new_score) < 20:
        return jsonify({"error": "Note Invalide"}), 400
    
    note = Note.query.get(note_id)
    if note:
        note.note = new_score
        db.session.commit()
        return jsonify({"success": True, "new_score": new_score})

    return jsonify({"error": "Note pas trouvee"}), 404


@general_controller.route("/cahier_de_texte")
def cahier_de_texte():
    """Loads the homework and agenda page for students and teachers."""
    if "user" not in session:
        return redirect(url_for("auth_controller.login"))

    role = session.get("role")
    eleve = Eleve.query.get(session["user"]) if role == "eleve" else None
    professeur = Professeur.query.get(session["user"]) if role == "professeur" else None
    agenda = [
        {"matiere": "Maths", "prof": "M. Dupont", "debut": "8H30", "fin": "9H30"},
        {"matiere": "Histoire", "prof": "Mme Lefevre", "debut": "10H00", "fin": "11H00"},
    ]
    devoirs = [
        {"matiere": "Maths", "contenu": "Exercices 3, 4 et 5 page 42"},
        {"matiere": "Histoire", "contenu": "Lire le chapitre sur la Révolution"},
    ]
    classes = Classe.query.all() if role == "professeur" else []

    return render_template("cahier_de_texte.html", role=role, eleve=eleve, professeur=professeur, agenda=agenda, devoirs=devoirs, classes=classes)

@general_controller.route("/vie_scolaire")
def vie_scolaire():
    """Loads the vie scolaire page for students and teachers."""
    if "user" not in session:
        return redirect(url_for("auth_controller.login"))

    role = session.get("role")
    eleve = Eleve.query.get(session["user"]) if role == "eleve" else None
    professeur = Professeur.query.get(session["user"]) if role == "professeur" else None
    prof_principal = Professeur.query.get(eleve.classe.prof_principal) if role == "eleve" else None
    classe_mates = Eleve.query.filter_by(classe_id=eleve.classe_id).all() if role == "eleve" else []
    notes = Note.query.filter_by(eleve_id=session["user"]).join(Matiere).all() if role == "eleve" else Note.query.all()

    return render_template("vie_scolaire.html", role=role, eleve=eleve, professeur=professeur, classe_mates=classe_mates, prof_principal=prof_principal, notes=notes)

@general_controller.route("/profile")
def profile():
    """Loads profile page for students and teachers."""
    if "user" not in session:
        return redirect(url_for("auth_controller.login"))

    role = session.get("role")
    user = Eleve.query.get(session["user"]) if role == "eleve" else Professeur.query.get(session["user"])
    classe = Classe.query.get(user.classe_id) if role == "eleve" else None
    professeurs = ProfMatiere.query.filter(ProfMatiere.matiere_id.in_([note.matiere_id for note in user.notes])).all() if role == "eleve" else None
    matieres = ProfMatiere.query.filter_by(professeur_id=user.id).all() if role == "professeur" else None

    return render_template("profile.html", role=role, user=user, classe=classe, professeurs=professeurs, matieres=matieres)


@general_controller.route("/communication")
def communication():
    """Loads the communication page."""
    return render_template("communication.html")
