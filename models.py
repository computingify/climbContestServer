from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Level table to store climbing levels
class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # U10, U12, U14, U16
    
# Climber table to store climber details
class Climber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    # Relationship with Level
    level = db.relationship('Level', backref=db.backref('climbers', lazy=True))

# Bloc table to store bloc details
class Bloc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bloc_id = db.Column(db.String(50), unique=True, nullable=False)

class UUIDMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100), unique=True, nullable=False)
    climber_name = db.Column(db.String(50), db.ForeignKey('climber.name'), nullable=True)
    bloc_id = db.Column(db.String(50), db.ForeignKey('bloc.bloc_id'), nullable=True)

# Many-to-Many table for climber and bloc (tracks successful climbs)
class ClimberBlocs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    climber_id = db.Column(db.Integer, db.ForeignKey('climber.id'), nullable=False)
    bloc_id = db.Column(db.Integer, db.ForeignKey('bloc.id'), nullable=False)

    # Relationships for easy querying
    climber = db.relationship('Climber', backref=db.backref('climber_blocs', lazy=True))
    bloc = db.relationship('Bloc', backref=db.backref('climber_blocs', lazy=True))

# Many-to-Many table for level and bloc (assigns blocs to levels)
class LevelBlocs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    bloc_id = db.Column(db.Integer, db.ForeignKey('bloc.id'), nullable=False)

    # Relationships for easy querying
    level = db.relationship('Level', backref=db.backref('level_blocs', lazy=True))
    bloc = db.relationship('Bloc', backref=db.backref('level_blocs', lazy=True))