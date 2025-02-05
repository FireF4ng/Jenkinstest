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
    
    try:
        with app.app_context():
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
                
            db.create_all()  # Ensure database schema exists before adding data
            
            add_admin_user()  # Always create admin user
            
            create_samples()  # Ensure sample users are added
                
            print("Database initialized successfully!")
            
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")

# Initialiser la base si elle n'existe pas encore
init_db()

if __name__ == "__main__":
    app.run(debug=True)  # Set debug to True for debugging


"""TODO
- Prof principal a classe
- Finir toute pages secondaires
- Tableau devoir a faire
- Tableau agenda (classe, matiere, matiere-prof, debut, fin)
- notes entre 1 et 20
- pages secondaires enlever search, enlever info perso (mettre dans profil) fusioner notes et viescolaire
- page communication = feedback normale
- heder/footer generale en html different
- enlever photo profil (mettre icone generale)
"""