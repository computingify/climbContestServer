from flask import Flask
from fbapp import create_app, db  # Import create_app and db

app = create_app()  # Create the app using the factory

@app.route('/')
def index():
    return "Hello world !"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables within the app context
    app.run()