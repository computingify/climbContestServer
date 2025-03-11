from flask_sqlalchemy import SQLAlchemy
from views import app
from . import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

db = SQLAlchemy(app)

# Climber table to store climber details
class Climber(db.Model, Base):
    __tablename__ = 'climber'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    bib = Column(Integer, unique=True, nullable=False)
    club = Column(String(50))
    category = Column(String(5))
    successes = relationship('Success', backref='climber', lazy=True)

class Success(db.Model, Base):
    __tablename__ = 'success'
    id = Column(Integer, primary_key=True)
    climber_id = Column(Integer, ForeignKey('climber.id'), nullable=False)
    bloc_id = Column(Integer, ForeignKey('bloc.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.current_timestamp())
    
class Bloc(db.Model, Base):
    __tablename__ = 'bloc'
    id = Column(Integer, primary_key=True)
    tag = Column(String(5), unique=True, nullable=False)
    number = Column(String(10), unique=True, nullable=False)
    level = Column(String(15))
    
class BlocCategory(db.Model, Base):
    __tablename__ = 'bloc_category'
    id = Column(Integer, primary_key=True)
    bloc_id = Column(Integer, ForeignKey('bloc.id'), nullable=False)
    category = Column(String(5), nullable=False)
    __table_args__ = (db.UniqueConstraint('bloc_id', 'category', name='unique_bloc_category'),)
    bloc = relationship('Bloc', backref=db.backref('bloc_categories', lazy=True))