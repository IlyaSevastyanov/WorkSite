import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    DB_SERVER = os.environ.get('DB_SERVER') or 'localhost'
    DB_NAME = os.environ.get('DB_NAME') or 'autobus'
    DB_USER = os.environ.get('DB_USER') or 'passenger'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '123'
    SECRET_KEY = os.environ.get('SECRET_KEY')