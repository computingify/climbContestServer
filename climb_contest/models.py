from .extensions import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Table
from sqlalchemy.orm import relationship

MAX_BLOC_VALUE = 1000

# Association table for Climber category and Bloc
climber_category_bloc = db.Table('climber_category_bloc',
    db.Column('category', String(50), primary_key=True),
    db.Column('bloc_id', Integer, db.ForeignKey('bloc.id'), primary_key=True)
)

# Climber table to store climber details
class Climber(db.Model):
    __tablename__ = 'climber'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    bib = db.Column(Integer, unique=True, nullable=False)
    club = db.Column(String(50))
    category = db.Column(String(50))
    score = db.Column(Integer, nullable=False, default=0)
    own_category_rank = db.Column(Integer, nullable=False, default=0)
    
    # Relations
    successes = relationship('Success', backref='climber', lazy=True)
    rankings = relationship('Ranking', backref='climber', lazy=True)
    blocs = relationship('Bloc', secondary=climber_category_bloc,
                         primaryjoin="Climber.category == climber_category_bloc.c.category",
                         secondaryjoin="Bloc.id == climber_category_bloc.c.bloc_id",
                         backref='categories')

    def to_dict(self):
        """Méthode utilitaire pour sérialiser l'objet Climber pour l'API."""
        return {
            "id": self.id,
            "name": self.name,
            "bib": self.bib,
            "club": self.club,
            "category": self.category,
            "score": self.score,
            "rank": self.own_category_rank,
        }

# Bloc table to store bloc details
class Bloc(db.Model):
    __tablename__ = 'bloc'
    id = db.Column(Integer, primary_key=True)
    tag = db.Column(String(50), unique=True, nullable=False) # The QR code
    number = db.Column(String(50), unique=True, nullable=False)

# Success table to store success details
class Success(db.Model):
    __tablename__ = 'success'
    id = db.Column(Integer, primary_key=True)
    climber_id = db.Column(Integer, db.ForeignKey('climber.id'), nullable=False)
    bloc_id = db.Column(Integer, db.ForeignKey('bloc.id'), nullable=False)
    timestamp = db.Column(DateTime, nullable=False, default=func.current_timestamp())
    
# Ranking table
class Ranking(db.Model):
    __tablename__ = 'ranking'
    climber_id = db.Column(Integer, db.ForeignKey('climber.id'), primary_key=True)
    category = db.Column(String(50), primary_key=True) # Catégorie (ex: "scratch", "U18 H")
    
    # ranking informations
    rank = db.Column(Integer, nullable=False) # Le rang dans cette catégorie
    score = db.Column(Integer, nullable=False) # Le score calculé (stocké pour référence)

    def to_dict(self):
        """Méthode utilitaire pour sérialiser l'objet Ranking pour l'API."""
        return {
            "id": self.climber.id,
            "name": self.climber.name,
            "bib": self.climber.bib,
            "club": self.climber.club,
            "category": self.category,
            "score": self.score,
            "rank": self.rank,
        }