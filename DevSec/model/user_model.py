from flask_sqlalchemy import SQLAlchemy
from datetime import date  # Import date from datetime module
from db.db import db

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
    mdp = db.Column(db.String(255), nullable=False)
    notes = db.relationship('Note', backref='eleve', lazy=True)

    def get_notes(self):
        return Note.query.filter_by(eleve_id=self.id).all()

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
    date = db.Column(db.Date, nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleves.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)

    def __repr__(self):
        return f"<Note {self.note}>"
class Professeur(db.Model):
    __tablename__ = 'professeurs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    mdp = db.Column(db.String(255), nullable=False)
    profs_matieres = db.relationship('ProfMatiere', backref='professeur', lazy=True)

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
                mdp='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")

def create_samples():
    try:
        # Only create samples if database is empty
        if not Eleve.query.first():
            # Create sample classe
            classe1 = Classe(nom="Classe 1")
            db.session.add(classe1)
            db.session.commit()

            # Create sample users
            eleves = [
                Eleve(username='eleve1', nom='Eleve', prenom='Un', classe_id=1, mdp='eleve1'),
                Eleve(username='eleve2', nom='Eleve', prenom='Deux', classe_id=1, mdp='eleve2'),
                Eleve(username='eleve3', nom='Eleve', prenom='Trois', classe_id=1, mdp='eleve3')
            ]
            db.session.bulk_save_objects(eleves)

            # Create sample Professeurs
            profs = [
                Professeur(username='prof1', nom='Prof', prenom='Un', mdp='prof1'),
                Professeur(username='prof2', nom='Prof', prenom='Deux', mdp='prof2')
            ]
            db.session.bulk_save_objects(profs)

            # Create sample matieres
            matieres = [
                Matiere(matiere='Maths'),
                Matiere(matiere='Francais')
            ]
            db.session.bulk_save_objects(matieres)
            db.session.commit()

            # Create sample notes
            notes = [
                Note(note=10, date=date(2021, 1, 1), matiere_id=1, eleve_id=1),
                Note(note=12, date=date(2021, 1, 1), matiere_id=2, eleve_id=1),
                Note(note=15, date=date(2021, 1, 1), matiere_id=1, eleve_id=2)
            ]
            db.session.bulk_save_objects(notes)

            # Create sample profs_matieres
            pm = [
                ProfMatiere(professeur_id=1, matiere_id=1),
                ProfMatiere(professeur_id=2, matiere_id=2)
            ]
            db.session.bulk_save_objects(pm)

            db.session.commit()
            print("Sample created!")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error creating samples: {str(e)}")
