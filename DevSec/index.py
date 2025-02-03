from flask import Flask
from model.user_model import *
from controller.main_controller import main_controller
import os

app = Flask(__name__, template_folder="view/templates", static_folder="view/static")
app.config.from_object("config.Config")

db.init_app(app)  # Initialize db with app

app.register_blueprint(main_controller)

def init_db():
    """Initialise la base SQLite avec les données de pronote.sql"""
    db_path = "db/database.db"
    
    if not os.path.exists(db_path):
        print("Initialisation de la base...")
        # Create the database file
        open(db_path, 'w').close()
        
        # Create all tables using SQLAlchemy
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
            create_samples()
            add_admin_user()
    else:
        print("La base de données existe déjà.")

# Initialiser la base si elle n'existe pas encore
init_db()

if __name__ == "__main__":
    app.run(debug=True)  # Set debug to True for debugging
