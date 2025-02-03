from flask import Flask
from model.user_model import *
from controller.main_controller import main_controller
import os

app = Flask(__name__, template_folder="view/templates", static_folder="view/static")
app.config.from_object("config.Config")

db.init_app(app)  # Initialize db with app

app.register_blueprint(main_controller)

def init_db():
    """Initialize the database"""
    db_dir = "db"
    db_path = os.path.join(db_dir, "database.db")
    
    try:
        with app.app_context():
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
                
            db.create_all()
            
            # Check if admin exists
            if not Eleve.query.filter_by(username='admin').first():
                add_admin_user()
            
            # Create samples only if no students exist
            if not Eleve.query.filter(Eleve.username != 'admin').first():
                create_samples()
                
            print("Database initialized successfully!")
            
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")

# Initialiser la base si elle n'existe pas encore
init_db()

if __name__ == "__main__":
    app.run(debug=True)  # Set debug to True for debugging
