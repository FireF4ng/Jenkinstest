from flask import render_template, redirect, url_for, session, request, jsonify
from model.user_model import Eleve, Professeur, Note, Classe, Matiere, ProfMatiere, db
from flask import Blueprint
import random
from datetime import date

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
    
    if session["user"] == "admin":
        return render_template("admin.html")

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

@main_controller.route("/admin/data")
def admin_data():
    if session.get("user") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    table = request.args.get("table")
    entry_id = request.args.get("id")
    
    model = {
        "eleves": Eleve,
        "professeurs": Professeur,
        "matieres": Matiere,
        "notes": Note,
        "classes": Classe,
        "profs_matieres": ProfMatiere
    }.get(table)
    
    if not model:
        return jsonify({"error": "Invalid table"}), 400
    
    if entry_id:
        entry = model.query.get(entry_id)
        if not entry:
            return jsonify({"error": "Entry not found"}), 404
        
        # Convert to dict and handle relationships
        entry_data = {col.name: getattr(entry, col.name) 
                     for col in entry.__table__.columns}
        
        # Handle special cases
        if table == "notes":
            entry_data["date"] = entry_data["date"].isoformat()
        
        return jsonify({"entry": entry_data})
    
    # Get all entries
    entries = model.query.all()
    entries_data = []
    
    for entry in entries:
        entry_data = {col.name: getattr(entry, col.name) 
                     for col in entry.__table__.columns}
        
        # Handle special cases
        if table == "notes":
            entry_data["date"] = entry_data["date"].isoformat()
        
        entries_data.append(entry_data)
    
    return jsonify({"entries": entries_data})

@main_controller.route("/admin/form")
def admin_form():
    if session.get("user") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    table = request.args.get("table")
    model = {
        "eleves": Eleve,
        "professeurs": Professeur,
        "matieres": Matiere,
        "notes": Note,
        "classes": Classe,
        "profs_matieres": ProfMatiere
    }.get(table)
    
    if not model:
        return jsonify({"error": "Invalid table"}), 400
    
    # Get column names excluding internal SQLAlchemy attributes
    fields = [col.name for col in model.__table__.columns if not col.name.startswith('_')]
    return jsonify(fields)

@main_controller.route("/admin/add", methods=["POST"])
def admin_add():
    if session.get("user") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    table = data["table"]
    entry_data = data["data"]
    
    model = {
        "eleves": Eleve,
        "professeurs": Professeur,
        "matieres": Matiere,
        "notes": Note,
        "classes": Classe,
        "profs_matieres": ProfMatiere
    }.get(table)
    
    if not model:
        return jsonify({"error": "Invalid table"}), 400
    
    try:
        # Handle special cases
        if table == "notes":
            entry_data["date"] = date.fromisoformat(entry_data["date"])
        
        new_entry = model(**entry_data)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"success": True, "id": new_entry.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@main_controller.route("/admin/delete", methods=["POST"])
def admin_delete():
    if session.get("user") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    table = data["table"]
    entry_id = data["id"]
    
    model = {
        "eleves": Eleve,
        "professeurs": Professeur,
        "matieres": Matiere,
        "notes": Note,
        "classes": Classe,
        "profs_matieres": ProfMatiere
    }.get(table)
    
    entry = model.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
