# Usefull file to initialized the database in case of the app executed by gunicorn (becausse it does not use the if __main__)

def on_starting(server):
    from main import app, db
    with app.app_context():
        db.create_all()