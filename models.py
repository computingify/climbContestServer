from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Climber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Bloc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bloc_id = db.Column(db.String(50), unique=True, nullable=False)

class UUIDMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100), unique=True, nullable=False)
    climber_name = db.Column(db.String(50), db.ForeignKey('climber.name'), nullable=True)
    bloc_id = db.Column(db.String(50), db.ForeignKey('bloc.bloc_id'), nullable=True)
