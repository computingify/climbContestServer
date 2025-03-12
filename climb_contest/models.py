from .extensions import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Climber table to store climber details
class Climber(db.Model, Base):
    __tablename__ = 'climber'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    bib = Column(Integer, unique=True, nullable=False)
    club = Column(String(50))
    category = Column(String(5))
    successes = relationship('Success', backref='climber', lazy=True)
    
class Bloc(db.Model):
    __tablename__ = 'bloc'
    id = db.Column(Integer, primary_key=True)
    tag = Column(String(50), unique=True, nullable=False)
    number = Column(String(50), unique=True, nullable=False)

class Success(db.Model, Base):
    __tablename__ = 'success'
    id = Column(Integer, primary_key=True)
    climber_id = Column(Integer, ForeignKey('climber.id'), nullable=False)
    bloc_id = Column(Integer, ForeignKey('bloc.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.current_timestamp())
