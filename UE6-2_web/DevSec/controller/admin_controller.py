from flask import Blueprint, request, session, jsonify, redirect, url_for, render_template
from flask_wtf.csrf import generate_csrf, validate_csrf
from model.user_model import Eleve, Professeur, Matiere, Note, Classe, ProfMatiere, Feedback, Devoir, Agenda, db
from datetime import datetime

admin_controller = Blueprint("admin_controller", __name__)

# Constants for repeated messages
INVALID_TABLE_MSG = "Invalid table"
ENTRY_NOT_FOUND_MSG = "Entry not found"
UNAUTHORIZED_MSG = "Unauthorized"

# Model mapping
MODEL = {
    "eleves": Eleve,
    "professeurs": Professeur,
    "matieres": Matiere,
    "notes": Note,
    "classes": Classe,
    "profs_matieres": ProfMatiere,
    "feedback": Feedback,
    "devoirs": Devoir,
    "agenda": Agenda
}

def validate_admin_access():
    if session.get("user") != 0:
        return jsonify({"error": UNAUTHORIZED_MSG}), 403
    return None

def get_table_model(table):
    return MODEL.get(table)

def handle_property_update(entry, key, value):
    if isinstance(getattr(type(entry), key, None), property):
        setattr(entry, key, value)
        return True
    return False

def process_column_value(table_model, key, value):
    try:
        column_type = getattr(table_model, key).property.columns[0].type
        if isinstance(column_type, db.Date):
            return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format for {key}")
    return value

@admin_controller.route("/admin")
def admin_dashboard():
    """Renders the admin dashboard."""
    if session.get("user") != 0:  # Ensures only admin has access
        return redirect(url_for("auth_controller.login"))
    
    return render_template("admin.html", csrf_token=generate_csrf())


# Updated admin_data route
@admin_controller.route("/admin/data")
def admin_data():
    if error := validate_admin_access():
        return error
    
    table = request.args.get("table")
    entry_id = request.args.get("id")
    table_model = get_table_model(table)
    
    if not table_model:
        return jsonify({"error": INVALID_TABLE_MSG}), 400
    
    if entry_id:
        return handle_single_entry(table_model, entry_id)
    
    return handle_table_query(table_model)

def handle_single_entry(table_model, entry_id):
    entry = table_model.query.get(entry_id)
    if not entry:
        return jsonify({"error": ENTRY_NOT_FOUND_MSG}), 404
    
    entry_data = {col.name: getattr(entry, col.name) for col in entry.__table__.columns}
    if table_model == Note:
        entry_data["date"] = entry_data["date"].isoformat()
    
    return jsonify({"entry": entry_data})

def handle_table_query(table_model):
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "")
    sort_order = request.args.get("order", "asc")
    
    query = table_model.query
    
    if search_query:
        query = apply_search_filter(query, table_model, search_query)
    
    if sort_by:
        query = apply_sorting(query, table_model, sort_by, sort_order)
    
    entries = query.all()
    result = [{col.name: getattr(entry, col.name) for col in table_model.__table__.columns} for entry in entries]
    
    return jsonify({"success": True, "entries": result})

def apply_search_filter(query, table_model, search_query):
    filters = []
    for column in table_model.__table__.columns:
        if column.type.python_type == str:
            filters.append(column.ilike(f"%{search_query}%"))
    return query.filter(db.or_(*filters))

def apply_sorting(query, table_model, sort_by, sort_order):
    column = getattr(table_model, sort_by, None)
    if column:
        return query.order_by(column.asc() if sort_order == "asc" else column.desc())
    return query


@admin_controller.route("/admin/form")
def admin_form():
    if session.get("user") != 0:
        return jsonify({"error": "Unauthorized"}), 403
    
    table = request.args.get("table")
    table_list = get_table_model(table)
    
    if not table_list:
        return jsonify({"error": INVALID_TABLE_MSG}), 400
    
    # Get column names excluding internal SQLAlchemy attributes
    fields = [col.name for col in table_list.__table__.columns if not col.name.startswith('_')]
    return jsonify(fields)


# Updated update_entry route
@admin_controller.route("/admin/update", methods=["POST"])
def update_entry():
    """Met à jour une entrée existante."""
    if error := validate_admin_access():
        return error
    
    data = request.json

    csrf_token = data.get("csrf_token")  # Récupération du token depuis la requête
    if not csrf_token or not validate_csrf(csrf_token):
        return jsonify({"success": False, "error": "Invalid CSRF token"}), 403
    
    table, entry_id, updates = data.get("table"), data.get("id"), data.get("updates")

    if not all([table, entry_id, updates]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    table_model = get_table_model(table)
    if not table_model:
        return jsonify({"success": False, "error": INVALID_TABLE_MSG}), 400

    entry = table_model.query.get(entry_id)
    if not entry:
        return jsonify({"success": False, "error": ENTRY_NOT_FOUND_MSG}), 404

    try:
        process_entry_data(entry, updates)
        db.session.commit()
        return jsonify({"success": True, "message": "Entry updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

def process_updates(entry, table_model, updates):
    for key, value in updates.items():
        if not hasattr(entry, key):
            continue
            
        if handle_property_update(entry, key, value):
            continue
            
        if key == "mdp_hash":
            handle_password_update(entry, value)
            continue
            
        try:
            processed_value = process_column_value(table_model, key, value)
            setattr(entry, key, processed_value)
        except ValueError as e:
            print(f"Erreur lors du traitement de {key}: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

def handle_password_update(entry, value):
    if isinstance(entry, (Eleve, Professeur)):
        entry.set_password(value)
    else:
        raise ValueError("Cannot update password for this entry")

# Similar refactoring for add_entry would follow the same pattern
@admin_controller.route("/admin/add", methods=["POST"])
def add_entry():
    """Ajoute une entrée à la base de données."""
    if error := validate_admin_access():
        return error
    
    data = request.json

    csrf_token = data.get("csrf_token")  # Récupération du token depuis la requête
    if not csrf_token or not validate_csrf(csrf_token):
        return jsonify({"success": False, "error": "Invalid CSRF token"}), 403

    table, entry_data = data.get("table"), data.get("data")

    if not table or not entry_data:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    table_model = get_table_model(table)
    if not table_model:
        return jsonify({"success": False, "error": INVALID_TABLE_MSG}), 400

    entry = table_model()
    
    try:
        process_entry_data(entry, entry_data)
        db.session.add(entry)
        db.session.commit()
        return jsonify({"success": True, "message": "Entry added successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

def process_entry_data(entry, entry_data):
    """Traite les données d'entrée avant de les enregistrer dans la base."""
    for key, value in entry_data.items():
        if hasattr(entry, key):
            if isinstance(getattr(type(entry), key, None), property):
                setattr(entry, key, value)
            elif key == "mdp_hash" and isinstance(entry, (Eleve, Professeur)):
                entry.set_password(value)
            else:
                setattr(entry, key, value)

def process_entry_data(entry, entry_data):
    """Traite les données d'entrée avant de les enregistrer dans la base."""
    for key, value in entry_data.items():
        if hasattr(entry, key):
            if isinstance(getattr(type(entry), key, None), property):
                setattr(entry, key, value)
            elif key == "mdp_hash" and isinstance(entry, (Eleve, Professeur)):
                entry.set_password(value)
            else:
                setattr(entry, key, value)


@admin_controller.route("/admin/delete", methods=["POST"])
def admin_delete():
    if session.get("user") != 0:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    table = data["table"]
    entry_id = data["id"]
    
    table_list = get_table_model(table)
    
    entry = table_list.query.get(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400