# Only for Gunicorn to create the app instance
from climb_contest import create_app

# Crée l'instance de l'application pour Gunicorn
app = create_app()

if __name__ == "__main__":
    # Ceci est utilisé seulement si vous lancez python wsgi.py en local
    app.run()