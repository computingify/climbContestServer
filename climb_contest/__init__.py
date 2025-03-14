from flask import Flask
from .config import Config
from .extensions import db
from .routes import main
from .google_sheets import google_sheet
import os

def create_app(config_name=None):
    app = Flask(__name__)
    app.register_blueprint(main)
    app.config.from_object(Config)
    
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    db.init_app(app)
    # Initialize the database with data from Google Sheets if not in testing mode
    if config_name != 'testing':
        if not os.path.exists('instance/database.db'):
            print("Initializing the database with data from Google Sheets")
            with app.app_context():
                db.create_all()  # Create the database tables
                from .google_sheets_reader import populate_bloc, populate_climbers # Import here to avoid circular dependency
                populate_bloc(google_sheet, db)
                populate_climbers(google_sheet, db)
    
    return app