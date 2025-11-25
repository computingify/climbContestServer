from .extensions import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Table
from sqlalchemy.orm import relationship

# Association table for Climber category and Bloc
climber_category_bloc = db.Table('climber_category_bloc',
    db.Column('category', String(5), primary_key=True),
    db.Column('bloc_id', Integer, db.ForeignKey('bloc.id'), primary_key=True)
)

# Climber table to store climber details
class Climber(db.Model):
    __tablename__ = 'climber'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    bib = db.Column(Integer, unique=True, nullable=False)
    club = db.Column(String(50))
    category = db.Column(String(5))
    score = db.Column(Integer, nullable=False, default=0)
    successes = relationship('Success', backref='climber', lazy=True)
    blocs = relationship('Bloc', secondary=climber_category_bloc,
                         primaryjoin="Climber.category == climber_category_bloc.c.category",
                         secondaryjoin="Bloc.id == climber_category_bloc.c.bloc_id",
                         backref='categories')

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