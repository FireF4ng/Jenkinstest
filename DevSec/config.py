import os

class Config:
    SECRET_KEY = "your_secret_key_here"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db/database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
