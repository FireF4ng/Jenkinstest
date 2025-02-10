from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from model.user_model import *
import random

general_controller = Blueprint("general_controller", __name__)


@general_controller.route("/student_dashboard")
def student_dashboard():
    """Loads student main menu with real agenda and homework from DB."""
    if "user" not in session or session["role"] != "eleve":
        return redirect(url_for("auth_controller.login"))

    eleve = Eleve.query.get(session["user"])
    if not eleve:
        return redirect(url_for("auth_controller.login"))

    role = "eleve"
    notes = eleve.get_notes()

    agenda = (
        Agenda.query
        .join(Matiere)
        .join(Professeur)
        .filter(Agenda.classe_id == eleve.classe_id)
        .all()
    )

    devoirs = (
        Devoir.query
        .join(Matiere)
        .filter(Devoir.matiere_id.in_([m.id for m in Matiere.query.all()]))
        .all()
    )

    return render_template("main.html", role=role, eleve=eleve, notes=notes, agenda=agenda, devoirs=devoirs)



@general_controller.route("/teacher_dashboard")
def teacher_dashboard():
    """Loads teacher dashboard with recent student grades and assigned agenda/work."""
    if "user" not in session or session["role"] != "professeur":
        return redirect(url_for("auth_controller.login"))

    professeur = Professeur.query.get(session["user"])
    if not professeur:
        return redirect(url_for("auth_controller.login"))

    role = "professeur"

    last_notes = (
        Note.query
        .join(Eleve)
        .join(Matiere)
        .join(ProfMatiere, ProfMatiere.matiere_id == Note.matiere_id)
        .filter(ProfMatiere.professeur_id == professeur.id)
        .order_by(Note.date.desc())
        .limit(5)
        .all()
    )

    agenda = (
        Agenda.query
        .join(Matiere)
        .join(Classe)
        .filter(Agenda.professeur_id == professeur.id)
        .all()
    )

    devoirs = (
        Devoir.query
        .join(Matiere)
        .filter(Devoir.professeur_id == professeur.id)
        .all()
    )

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
    """Loads the homework and agenda page dynamically."""
    if "user" not in session:
        return redirect(url_for("auth_controller.login"))

    role = session["role"]

    # Fetch agenda for the student's class or professor's subjects
    if role == "eleve":
        eleve = Eleve.query.get(session["user"])
        agenda = Agenda.query.filter_by(classe_id=eleve.classe_id).join(Matiere).join(Professeur).join(Classe).all()
        devoirs = Devoir.query.filter(Devoir.matiere_id.in_([m.id for m in Matiere.query.all()])).join(Matiere).all()
    else:
        professeur = Professeur.query.get(session["user"])
        agenda = Agenda.query.filter_by(professeur_id=professeur.id).join(Matiere).join(Professeur).join(Classe).all()
        devoirs = Devoir.query.filter_by(professeur_id=professeur.id).join(Matiere).all()

    return render_template("cahier_de_texte.html", role=role, agenda=agenda, devoirs=devoirs)

@general_controller.route("/vie_scolaire")
def vie_scolaire():
    """Loads the vie scolaire page for students and teachers."""
    if "user" not in session:
        return redirect(url_for("auth_controller.login"))

    role = session.get("role")
    eleve = Eleve.query.get(session["user"]) if role == "eleve" else None
    professeur = Professeur.query.get(session["user"]) if role == "professeur" else None
    prof_principal = Professeur.query.get(eleve.classe.prof_principal) if role == "eleve" else None
    classe_mates = Eleve.query.filter_by(classe_id=eleve.classe_id).all() if role == "eleve" else Eleve.query.join(Classe).filter(Classe.prof_principal == professeur.id).all()
    notes = Note.query.filter_by(eleve_id=session["user"]).join(Matiere).all() if role == "eleve" else Note.query.all()

    return render_template("vie_scolaire.html", role=role, eleve=eleve, professeur=professeur, classe_mates=classe_mates, prof_principal=prof_principal, notes=notes)

@general_controller.route("/profile")
def profile():
    """Loads profile page for students and teachers."""
    if "user" not in session:
        return redirect(url_for("auth_controller.login"))

    role = session.get("role")
    user = Eleve.query.get(session["user"]) if role == "eleve" else Professeur.query.get(session["user"])
    classe = Classe.query.get(user.classe_id) if role == "eleve" else Classe.query.filter_by(prof_principal=user.id).first()
    professeurs = ProfMatiere.query.filter(ProfMatiere.matiere_id.in_([note.matiere_id for note in user.notes])).all() if role == "eleve" else None
    matieres = ProfMatiere.query.filter_by(professeur_id=user.id).all() if role == "professeur" else None

    return render_template("profile.html", role=role, user=user, classe=classe, professeurs=professeurs, matieres=matieres)


@general_controller.route("/communication", methods=["GET", "POST"])
def communication():
    """Loads the communication page."""
    if "user" not in session:
        return redirect(url_for("auth_controller.login"))
    
    if request.method == "POST":
        message = request.form.get("message")
        if message:
            feedback = Feedback(user_id=session["user"], user_role=session["role"], message=message)
            db.session.add(feedback)
            db.session.commit()
            return jsonify({"success": True, "message": "Feedback envoyé avec succès!"})
        
    return render_template("communication.html")

@general_controller.route("/update_credentials", methods=["POST"])
def update_credentials():
    if "user" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 403

    data = request.json
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    user = Eleve.query.get(session["user"]) or Professeur.query.get(session["user"])

    if not user or not user.check_password(old_password):
        return jsonify({"success": False, "error": "Invalid current credentials"}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({"success": True, "message": "Credentials updated successfully"})
