from flask import Blueprint, request, session, jsonify, redirect, url_for, render_template
from model.user_model import *
from datetime import datetime

admin_controller = Blueprint("admin_controller", __name__)
global model
model = {
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

@admin_controller.route("/admin")
def admin_dashboard():
    """Renders the admin dashboard."""
    if session.get("user") != 0:  # Ensures only admin has access
        return redirect(url_for("auth_controller.login"))
    
    return render_template("admin.html")

@admin_controller.route("/admin/data")
def admin_data():
    if session.get("user") != 0:
        return jsonify({"error": "Unauthorized"}), 403
    
    table = request.args.get("table")
    entry_id = request.args.get("id")
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "")
    sort_order = request.args.get("order", "asc")
    
    table_list = model.get(table)
    
    if not table_list:
        return jsonify({"error": "Invalid table"}), 400
    
    if entry_id:
        entry = table_list.query.get(entry_id)
        if not entry:
            return jsonify({"error": "Entry not found"}), 404
        
        # Convert to dict and handle relationships
        entry_data = {col.name: getattr(entry, col.name) 
                     for col in entry.__table__.columns}
        
        # Handle special cases
        if table == "notes":
            entry_data["date"] = entry_data["date"].isoformat()
        
        return jsonify({"entry": entry_data})
    
    query = table_list.query

    # Search functionality
    if search_query:
        filters = []
        for column in table_list.__table__.columns:
            if column.type.python_type == str:
                filters.append(column.ilike(f"%{search_query}%"))
        query = query.filter(db.or_(*filters))

    # Sorting functionality
    if sort_by:
        column = getattr(table_list, sort_by, None)
        if column:
            query = query.order_by(column.asc() if sort_order == "asc" else column.desc())

    entries = query.all()
    result = [{col.name: getattr(entry, col.name) for col in table_list.__table__.columns} for entry in entries]

    return jsonify({"success": True, "entries": result})

@admin_controller.route("/admin/form")
def admin_form():
    if session.get("user") != 0:
        return jsonify({"error": "Unauthorized"}), 403
    
    table = request.args.get("table")
    table_list = model.get(table)
    
    if not table_list:
        return jsonify({"error": "Invalid table"}), 400
    
    # Get column names excluding internal SQLAlchemy attributes
    fields = [col.name for col in table_list.__table__.columns if not col.name.startswith('_')]
    return jsonify(fields)


@admin_controller.route("/admin/update", methods=["POST"])
def update_entry():
    data = request.json
    table = data.get("table")
    entry_id = data.get("id")
    updates = data.get("updates")

    if not table or not entry_id or not updates:
        return jsonify({"success": False, "error": "Missing required fields"}), 400


    table_list = model.get(table)
    if not table_list:
        return jsonify({"success": False, "error": "Invalid table"}), 400

    # Find the entry and update it
    entry = table_list.query.get(entry_id)
    if not entry:
        return jsonify({"success": False, "error": "Entry not found"}), 404

    for key, value in updates.items():
        if hasattr(entry, key):
            column_type = getattr(table_list, key).property.columns[0].type

            # Convert string to date if the column is a Date type
            if isinstance(column_type, db.Date):
                try:
                    value = datetime.strptime(value, "%Y-%m-%d").date()  # Ensure proper format
                except ValueError:
                    return jsonify({"success": False, "error": f"Invalid date format for {key}"}), 400

            if key == "mdp_hash":
                if session.get("role") == "eleve":
                    value = Eleve.set_password(value)
                elif session.get("role") == "professeur":
                    value = Professeur.set_password(value)
            setattr(entry, key, value)

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Entry updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500



@admin_controller.route("/admin/add", methods=["POST"])
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

    table_list = model.get(table)
    if not table_list:
        return jsonify({"success": False, "error": "Invalid table"}), 400

    entry = table_list(**entry_data)
    db.session.add(entry)
    db.session.commit()
    return jsonify({"success": True, "message": "Entry added successfully"})

@admin_controller.route("/admin/delete", methods=["POST"])
def admin_delete():
    if session.get("user") != 0:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    table = data["table"]
    entry_id = data["id"]
    
    table_list = model.get(table)
    
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