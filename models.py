from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Climber table to store climber details
class Climber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    bib = db.Column(db.Integer, unique=True, nullable=False)
    club = db.Column(db.String(50))
    category = db.Column(db.String(5))
    
class Bloc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50), unique=True, nullable=False)
    number = db.Column(db.String(50), unique=True, nullable=False)

class UUIDMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100), unique=True, nullable=False)
    climber_bib = db.Column(db.String(50), db.ForeignKey('climber.bib'), nullable=True)
    bloc_number = db.Column(db.String(50), db.ForeignKey('bloc.number'), nullable=True)
