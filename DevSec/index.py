from flask import Flask
from flask_wtf.csrf import CSRFProtect
from extensions import limiter
from model.user_model import db, add_admin_user, create_samples
from controller.auth_controller import auth_controller
from controller.admin_controller import admin_controller
from controller.general_controller import general_controller
import os

app = Flask(__name__, template_folder="view/templates", static_folder="view/static")
app.config.from_object("config.Config")

# Initialise Flask-Limiter avec l'application
limiter.init_app(app)

csrf = CSRFProtect(app) # Initialize CSRF protection

db.init_app(app)  # Initialize database

# Register controllers
app.register_blueprint(auth_controller)
app.register_blueprint(admin_controller)
app.register_blueprint(general_controller)

def init_db():
    """Initialize the database"""
    db_dir = "db"
    try:
        with app.app_context():
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
                
            db.create_all()  # Ensure database schema exists
            add_admin_user()  # Create admin user
            create_samples()  # Ensure sample users are added
                
            print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")

init_db()  # Initialize the database on start

if __name__ == "__main__":
    app.run(debug=True)  # Debug mode for development



"""TODO:
- Commenter le code et verifier si tout nom variables correct
"""