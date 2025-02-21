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
