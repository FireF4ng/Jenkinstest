from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Eleve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    mdp = db.Column(db.String(255), nullable=False)

    def get_notes(self):
        return Note.query.filter_by(eleve_id=self.id).all()

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleves.id'), nullable=False)

    def __repr__(self):
        return f"<Note {self.note}>"
