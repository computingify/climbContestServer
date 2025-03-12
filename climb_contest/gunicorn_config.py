# Usefull file to initialized the database in case of the app executed by gunicorn (becausse it does not use the if __main__)
from climb_contest import create_app, db
from climb_contest.google_sheets import GoogleSheet

def on_starting(server):
    app = create_app()  # Create the app
    with app.app_context():
        print("Database Creation and populating...")
        google_sheet = GoogleSheet()  # Instantiate GoogleSheet
        # Create the app with google_sheet to initialize the database
        app = create_app(google_sheet=google_sheet)
        with app.app_context():
            db.create_all()