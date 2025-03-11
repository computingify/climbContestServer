from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()  # Initialize SQLAlchemy *without* the app

def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['TESTING'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    db.init_app(app)  # Initialize SQLAlchemy *with* the app
    return app

from . import models  # Import models *after* app and db are initialized