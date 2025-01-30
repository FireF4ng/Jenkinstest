from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os

app = Flask(__name__)
app.config.from_object("config.Config")

db = SQLAlchemy(app)

def init_db():
    """Initialise la base SQLite avec les données de pronote.sql"""
    db_path = "instance/database.db"
    sql_file = "instance/pronote.sql"
    
    if not os.path.exists(db_path):
        print("Initialisation de la base...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        cursor.executescript(sql_script)
        conn.commit()
        conn.close()
        print("Base de données initialisée.")
    else:
        print("La base de données existe déjà.")

# Initialiser la base si elle n'existe pas encore
init_db()

if __name__ == "__main__":
    app.run(debug=True)
