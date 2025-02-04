from flask import render_template, redirect, url_for, session, request, jsonify
from model.user_model import Eleve, Professeur, Note, Classe, Matiere, ProfMatiere, db
from flask import Blueprint
import random
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

main_controller = Blueprint("main_controller", __name__)

@main_controller.route("/")
def home():
    if "user" in session:
        return redirect(url_for("main_controller.main_menu"))
    return redirect(url_for("main_controller.login"))

@main_controller.route("/login", methods=["GET", "POST"])
def login():
    message = "Veuillez entrer votre identifiant, mot de passe et clé secrète"
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        secret_key = request.form.get("secret_key")

        # Check if user exists in either Eleve or Professeur table
        user = Eleve.query.filter_by(username=username).first() or Professeur.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.secret_key == secret_key:
            session["user"] = user.username
            session["role"] = "eleve" if isinstance(user, Eleve) else "professeur"
            return redirect(url_for("main_controller.main_menu"))
        
        message = "Identifiants incorrects ou clé secrète invalide"
    
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
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "")
    sort_order = request.args.get("order", "asc")
    
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
    
    query = model.query

    # Search functionality
    if search_query:
        filters = []
        for column in model.__table__.columns:
            if column.type.python_type == str:
                filters.append(column.ilike(f"%{search_query}%"))
        query = query.filter(db.or_(*filters))

    # Sorting functionality
    if sort_by:
        column = getattr(model, sort_by, None)
        if column:
            query = query.order_by(column.asc() if sort_order == "asc" else column.desc())

    entries = query.all()
    result = [{col.name: getattr(entry, col.name) for col in model.__table__.columns} for entry in entries]

    return jsonify({"success": True, "entries": result})

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


@main_controller.route("/admin/update", methods=["POST"])
def update_entry():
    data = request.json
    table = data.get("table")
    entry_id = data.get("id")
    updates = data.get("updates")

    if not table or not entry_id or not updates:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    # Map table names to models
    model_mapping = {
        "eleves": Eleve,
        "professeurs": Professeur,
        "matieres": Matiere,
        "notes": Note,
        "classes": Classe,
        "profs_matieres": ProfMatiere
    }

    model = model_mapping.get(table)
    if not model:
        return jsonify({"success": False, "error": "Invalid table"}), 400

    # Find the entry and update it
    entry = model.query.get(entry_id)
    if not entry:
        return jsonify({"success": False, "error": "Entry not found"}), 404

    for key, value in updates.items():
        if hasattr(entry, key):
            setattr(entry, key, value)

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Entry updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500



@main_controller.route("/admin/add", methods=["POST"])
def add_entry():
    data = request.json
    table = data.get("table")
    entry_data = data.get("data")

    if not table or not entry_data:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    if "date" in entry_data:
        try:
            entry_data["date"] = datetime.strptime(entry_data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format"}), 400

    model_mapping = {
        "eleves": Eleve,
        "professeurs": Professeur,
        "matieres": Matiere,
        "notes": Note,
        "classes": Classe,
        "profs_matieres": ProfMatiere
    }

    model = model_mapping.get(table)
    if not model:
        return jsonify({"success": False, "error": "Invalid table"}), 400

    entry = model(**entry_data)
    db.session.add(entry)
    db.session.commit()
    return jsonify({"success": True, "message": "Entry added successfully"})

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

@main_controller.route("/update_credentials", methods=["POST"])
def update_credentials():
    if "user" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 403

    data = request.json
    old_password = data.get("old_password")
    old_secret = data.get("old_secret")
    new_password = data.get("new_password")
    new_secret = data.get("new_secret")

    if not old_password or not old_secret or not new_password or not new_secret:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    user = Eleve.query.filter_by(username=session["user"]).first() or Professeur.query.filter_by(username=session["user"]).first()
    
    if not user or not check_password_hash(user.mdp, old_password) or user.secret_key != old_secret:
        return jsonify({"success": False, "error": "Invalid current credentials"}), 400

    # Update credentials
    user.mdp = generate_password_hash(new_password)
    user.secret_key = new_secret  # Ensure new secret is unique
    db.session.commit()

    return jsonify({"success": True, "message": "Credentials updated successfully"})