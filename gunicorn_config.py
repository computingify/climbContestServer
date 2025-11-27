# Usefull file to initialized the database in case of the app executed by gunicorn (becausse it does not use the if __main__)
from climb_contest import create_app, db

def on_starting(server):
    print("Server startup in progress ...")
    app = create_app()
    with app.app_context():
        print("Server context app started. READY")