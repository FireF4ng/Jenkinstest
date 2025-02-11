from flask import Blueprint, request, session, jsonify, redirect, url_for, render_template
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
    
    return render_template("admin.html")


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
    data = request.json
    table = data.get("table")
    entry_id = data.get("id")
    updates = data.get("updates")

    if not all([table, entry_id, updates]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    table_model = get_table_model(table)
    if not table_model:
        return jsonify({"success": False, "error": INVALID_TABLE_MSG}), 400

    entry = table_model.query.get(entry_id)
    if not entry:
        return jsonify({"success": False, "error": ENTRY_NOT_FOUND_MSG}), 404

    try:
        process_updates(entry, table_model, updates)
        db.session.commit()
        return jsonify({"success": True, "message": "Entry updated successfully"})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
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
    data = request.json
    table = data.get("table")
    entry_data = data.get("data")

    if not table or not entry_data:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    table_list = get_table_model(table)
    if not table_list:
        return jsonify({"success": False, "error": INVALID_TABLE_MSG}), 400

    # Create the entry object
    entry = table_list()

    # Iterate through the data and set attributes
    for key, value in entry_data.items():
        if hasattr(entry, key):
            # Handle properties (nom and prenom)
            if isinstance(getattr(type(entry), key, None), property):
                setattr(entry, key, value)
                continue

            # Handle regular columns
            column_type = getattr(table_list, key).property.columns[0].type

            # Convert string to date if the column is a Date type
            if isinstance(column_type, db.Date):
                try:
                    value = datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    return jsonify({"success": False, "error": f"Invalid date format for {key}"}), 400

            # Hash passwords correctly
            if key == "mdp_hash":
                if isinstance(entry, Eleve) or isinstance(entry, Professeur):
                    entry.set_password(value)
                else:
                    return jsonify({"success": False, "error": "Cannot update password for this entry"}), 400
            else:
                setattr(entry, key, value)

    try:
        db.session.add(entry)
        db.session.commit()
        return jsonify({"success": True, "message": "Entry added successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


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