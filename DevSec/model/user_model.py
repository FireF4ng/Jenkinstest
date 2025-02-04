from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  # Import date from datetime module
from db.db import db
import secrets
import hashlib
import os

class Classe(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    eleves = db.relationship('Eleve', backref='classe', lazy=True)

class Eleve(db.Model):
    __tablename__ = 'eleves'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    mdp_hash = db.Column(db.String(255), nullable=False)
    secret_key = db.Column(db.String(32), unique=True, nullable=False, default=lambda: secrets.token_hex(16))
    
    notes = db.relationship('Note', backref='eleve', lazy=True)

    def set_password(self, password):
        """Hash the password using the secret key"""
        salt = os.urandom(16)  # Generate a random salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), self.secret_key.encode() + salt, 100000)
        self.mdp_hash = salt.hex() + key.hex()  # Store salt + hash

    def check_password(self, password):
        """Check if the password matches the stored hash"""
        salt = bytes.fromhex(self.mdp_hash[:32])  # Extract the salt
        stored_key = self.mdp_hash[32:]  # Extract the hashed password
        test_key = hashlib.pbkdf2_hmac('sha256', password.encode(), self.secret_key.encode() + salt, 100000)
        return test_key.hex() == stored_key  # Compare hashes

class Professeur(db.Model):
    __tablename__ = 'professeurs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    mdp_hash = db.Column(db.String(255), nullable=False)
    secret_key = db.Column(db.String(32), unique=True, nullable=False, default=lambda: secrets.token_hex(16))
    
    profs_matieres = db.relationship('ProfMatiere', backref='professeur', lazy=True)

    def set_password(self, password):
        """Hash the password using the secret key"""
        salt = os.urandom(16)  
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), self.secret_key.encode() + salt, 100000)
        self.mdp_hash = salt.hex() + key.hex()

    def check_password(self, password):
        """Check if the password matches the stored hash"""
        salt = bytes.fromhex(self.mdp_hash[:32])
        stored_key = self.mdp_hash[32:]
        test_key = hashlib.pbkdf2_hmac('sha256', password.encode(), self.secret_key.encode() + salt, 100000)
        return test_key.hex() == stored_key

class Matiere(db.Model):
    __tablename__ = 'matieres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matiere = db.Column(db.String(100), unique=True, nullable=False)
    notes = db.relationship('Note', backref='matiere', lazy=True)
    profs_matieres = db.relationship('ProfMatiere', backref='matiere', lazy=True)

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)  # Ensure default value is a date object
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleves.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)

    def __repr__(self):
        return f"<Note {self.note}>"

class ProfMatiere(db.Model):
    __tablename__ = 'profs_matieres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    professeur_id = db.Column(db.Integer, db.ForeignKey('professeurs.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)


def add_admin_user():
    try:
        if not Eleve.query.filter_by(username='admin').first():
            admin = Eleve(
                username='admin', 
                nom='Admin', 
                prenom='User', 
                classe_id=1, 
                secret_key="adminkey"  # Fixed secret key for admin
            )
            admin.set_password("admin")  # Hash password with secret key
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created! Secret Key: {admin.secret_key}")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")

def create_samples():
    try:
        with db.session.no_autoflush:  # Prevents issues with foreign key constraints
            # Ensure we only create samples if no users exist
            if Eleve.query.count() == 0 and Professeur.query.count() == 0:
                # Create sample class
                classe1 = Classe(nom="Classe 1")
                db.session.add(classe1)
                db.session.commit()  # Commit the class so foreign key references work

                # Create sample students
                eleves = []
                for i in range(1, 4):
                    eleve = Eleve(username=f'eleve{i}', nom='Eleve', prenom=f'Num{i}', classe_id=classe1.id)
                    eleve.set_password(f'eleve{i}')  # Hash password with secret key
                    eleves.append(eleve)

                db.session.bulk_save_objects(eleves)

                # Create sample professors
                profs = []
                for i in range(1, 3):
                    prof = Professeur(username=f'prof{i}', nom='Prof', prenom=f'Num{i}')
                    prof.set_password(f'prof{i}')  # Hash password with secret key
                    profs.append(prof)

                db.session.bulk_save_objects(profs)

                # Create sample subjects
                matieres = [
                    Matiere(matiere='Maths'),
                    Matiere(matiere='Francais')
                ]
                db.session.bulk_save_objects(matieres)
                db.session.commit()  # Commit subjects before assigning notes

                # Assign random notes to students
                notes = [
                    Note(note=10, date=datetime.utcnow().date(), matiere_id=1, eleve_id=1),
                    Note(note=12, date=datetime.utcnow().date(), matiere_id=2, eleve_id=1),
                    Note(note=15, date=datetime.utcnow().date(), matiere_id=1, eleve_id=2)
                ]
                db.session.bulk_save_objects(notes)

                db.session.commit()  # Final commit for all data

                print("Sample data created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating samples: {str(e)}")