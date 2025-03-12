from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config  # Assuming you have a config.py in src

db = SQLAlchemy()
        
def create_app(config_name=None, google_sheet=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['TESTING'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    db.init_app(app)
    
    # Initialize the database with data from Google Sheets if not in testing mode
    if config_name != 'testing' and google_sheet:
        with app.app_context():
            db.create_all()  # Create the database tables
            from .google_sheets_reader import populate_bloc, populate_climbers # Import here to avoid circular dependency
            populate_bloc(google_sheet, db)
            populate_climbers(google_sheet, db)
    
    return app

from . import models  # Import models after app and db are initialized