from db.db import db  # Import db from db.py
from datetime import date  # Import date from datetime module

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
    admin = Eleve(id=0, username='admin', nom='Admin', prenom='User', classe_id=1, mdp='admin')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created!")

def create_samples():
    # Create sample users
    eleve1 = Eleve(username='eleve1', nom='Eleve', prenom='Un', classe_id=1, mdp='eleve1')
    eleve2 = Eleve(username='eleve2', nom='Eleve', prenom='Deux', classe_id=1, mdp='eleve2')
    eleve3 = Eleve(username='eleve3', nom='Eleve', prenom='Trois', classe_id=1, mdp='eleve3')
    db.session.add(eleve1)
    db.session.add(eleve2)
    db.session.add(eleve3)

    # Create sample Professeurs
    prof1 = Professeur(username='prof1', nom='Prof', prenom='Un', mdp='prof1')
    prof2 = Professeur(username='prof2', nom='Prof', prenom='Deux', mdp='prof2')
    db.session.add(prof1)
    db.session.add(prof2)

    # Create sample matieres
    matiere1 = Matiere(matiere='Maths')
    matiere2 = Matiere(matiere='Francais')
    db.session.add(matiere1)
    db.session.add(matiere2)

    note1 = Note(note=10, date=date(2021, 1, 1), matiere_id=1, eleve_id=1)
    note2 = Note(note=12, date=date(2021, 1, 1), matiere_id=2, eleve_id=1)
    note3 = Note(note=15, date=date(2021, 1, 1), matiere_id=1, eleve_id=2)
    db.session.add(note1)
    db.session.add(note2)
    db.session.add(note3)

    # Create sample profs_matieres
    prof_matiere1 = ProfMatiere(professeur_id=1, matiere_id=1)
    prof_matiere2 = ProfMatiere(professeur_id=2, matiere_id=2)
    db.session.add(prof_matiere1)
    db.session.add(prof_matiere2)

    db.session.commit()
    print("Sample created!")
    db.session.close()
