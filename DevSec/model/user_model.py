from datetime import datetime  # Import date from datetime module
from db.db import db
import hashlib
import os

class Eleve(db.Model):
    __tablename__ = 'eleves'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    mdp_hash = db.Column(db.String(255), nullable=False)
    
    notes = db.relationship('Note', backref='eleve', lazy=True)

    def set_password(self, password):
        """Hash the password"""
        salt = os.urandom(16)  # Generate a random salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        self.mdp_hash = salt.hex() + key.hex()  # Store salt + hash

    def check_password(self, password):
        """Check if the password matches the stored hash"""
        if not self.mdp_hash or len(self.mdp_hash) < 64:
            return False
        
        try:
            salt = bytes.fromhex(self.mdp_hash[:32])
            stored_key = self.mdp_hash[32:]
            test_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return test_key.hex() == stored_key
        except ValueError:
            return False

    def get_notes(self):
        return Note.query.filter_by(eleve_id=self.id).all()

class Professeur(db.Model):
    __tablename__ = 'professeurs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    mdp_hash = db.Column(db.String(255), nullable=False)
    
    profs_matieres = db.relationship('ProfMatiere', backref='professeur', lazy=True)

    def set_password(self, password):
        """Hash the password"""
        salt = os.urandom(16)  
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        self.mdp_hash = salt.hex() + key.hex()

    def check_password(self, password):
        """Check if the password matches the stored hash"""
        salt = bytes.fromhex(self.mdp_hash[:32])
        stored_key = self.mdp_hash[32:]
        test_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return test_key.hex() == stored_key
    
class Classe(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    eleves = db.relationship('Eleve', backref='classe', lazy=True)
    prof_principal = db.Column(db.Integer, db.ForeignKey('professeurs.id', ondelete='RESTRICT', onupdate='RESTRICT'))

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
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleves.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)

    __table_args__ = (
        db.CheckConstraint('note BETWEEN 0 AND 20', name='check_note_range'),
    )

    def __repr__(self):
        return f"<Note {self.note}>"

class ProfMatiere(db.Model):
    __tablename__ = 'profs_matieres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    professeur_id = db.Column(db.Integer, db.ForeignKey('professeurs.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)

class Devoir(db.Model):
    __tablename__ = 'devoirs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    professeur_id = db.Column(db.Integer, db.ForeignKey('professeurs.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    contenu = db.Column(db.Text, nullable=False)

class Agenda(db.Model):
    __tablename__ = 'agenda'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    professeur_id = db.Column(db.Integer, db.ForeignKey('professeurs.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    debut = db.Column(db.String(10), nullable=False)
    fin = db.Column(db.String(10), nullable=False)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('eleves.id' or 'professeurs.id', ondelete='CASCADE'), nullable=False)
    user_role = db.Column(db.String(10), nullable=False)
    message = db.Column(db.Text, nullable=False)


def add_admin_user():
    try:
        if not Eleve.query.filter_by(username='admin').first():
            admin = Eleve(
                username='admin', 
                nom='Admin', 
                prenom='User', 
                classe_id=1, 
                id=0
            )
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")

def create_samples():
    try:
        if not Eleve.query.filter_by(id=1).first() or not Professeur.query.filter_by(id=1).first():
            with db.session.no_autoflush:

                classe1 = Classe(nom="Classe 1", prof_principal=1)
                db.session.add(classe1)
                db.session.commit()

                eleves = []
                for i in range(1, 4):
                    eleve = Eleve(username=f'eleve{i}', nom='Eleve', prenom=f'Num{i}', classe_id=classe1.id)
                    eleve.set_password(f'eleve{i}')
                    eleves.append(eleve)
                db.session.bulk_save_objects(eleves)

                profs = []
                for i in range(1, 3):
                    prof = Professeur(username=f'prof{i}', nom='Prof', prenom=f'Num{i}')
                    prof.set_password(f'prof{i}')
                    profs.append(prof)
                db.session.bulk_save_objects(profs)

                matieres = [
                    Matiere(matiere='Maths'),
                    Matiere(matiere='Francais')
                ]
                db.session.bulk_save_objects(matieres)
                db.session.commit()

                notes = [
                    Note(note=10, date=datetime.utcnow().date(), matiere_id=1, eleve_id=1),
                    Note(note=12, date=datetime.utcnow().date(), matiere_id=2, eleve_id=1),
                    Note(note=15, date=datetime.utcnow().date(), matiere_id=1, eleve_id=2)
                ]
                db.session.bulk_save_objects(notes)
                db.session.commit()

                prof_matieres = [
                    ProfMatiere(professeur_id=1, matiere_id=1),
                    ProfMatiere(professeur_id=2, matiere_id=2)
                ]
                db.session.bulk_save_objects(prof_matieres)
                db.session.commit()

                devoir = Devoir(matiere_id=1, professeur_id=1, contenu="Faire les exercices 1 et 2 de la page 10")
                db.session.add(devoir)
                db.session.commit()

                agenda = Agenda(classe_id=1, matiere_id=1, professeur_id=1, debut="08:00", fin="09:00")
                db.session.add(agenda)
                db.session.commit()

                print("Sample data created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating samples: {str(e)}")