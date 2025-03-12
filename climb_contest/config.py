import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'FesC9cBSuadndevkv0vBY'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add other configuration variables here