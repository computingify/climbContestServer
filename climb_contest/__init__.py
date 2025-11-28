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
    database_url = os.environ.get('DATABASE_URL')
    
    # Par défaut, nous utilisons SQLite (Local/Fallback)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    # Options SQLite : check_same_thread est NÉCESSAIRE pour SQLite dans un environnement multithread
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"check_same_thread": False}}
    print("INFO: Connexion à SQLite (Mode Local/Fallback).")
    
    # Si nous sommes en mode 'testing', utilisons SQLite en mémoire sans options
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # In-memory database for testing
        # Supprimer les options d'engine car non pertinentes pour la DB en mémoire de test
        if 'SQLALCHEMY_ENGINE_OPTIONS' in app.config:
             del app.config['SQLALCHEMY_ENGINE_OPTIONS']
        print("INFO: Connexion à SQLite en RAM pour les tests unitaires.")

    # Si DATABASE_URL est défini (c'est le cas sur Render), nous utilisons PostgreSQL
    elif database_url:
        # Remplacement requis par SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        # 🚨 C'EST LA PARTIE CRUCIALE : supprimer les options SQLite
        if 'SQLALCHEMY_ENGINE_OPTIONS' in app.config:
            del app.config['SQLALCHEMY_ENGINE_OPTIONS']
            
        print("INFO: Connexion à PostgreSQL.")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    # Initialize the database with data from Google Sheets if not in testing mode
    if config_name != 'testing':
        google_sheet.initialize()
        if not os.path.exists('instance/database.db'):
            print("Initializing the database with data from Google Sheets")
            with app.app_context():
                db.create_all()  # Create the database tables
                from .google_sheets_reader import populate_bloc, populate_climbers # Import here to avoid circular dependency
                populate_climbers(google_sheet, db)
                populate_bloc(google_sheet, db)
                
    # Start processor thread
    from .results.processor import Processor
    app.processor = Processor(app)
    app.processor.start()
    
    return app