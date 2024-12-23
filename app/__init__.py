from flask import Flask
from flask_bootstrap5 import Bootstrap5
from app.config import Config

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config.from_object(Config)

from app import routes
from app import flights
from app import buses
from app import stops
from app import trail
from app import forms
from app import register
from app import login
from app import profile
from app import alltrail
from app import update_profile
from app import update_trail
from app import update_trip
from app import notification
from app import update_flight
from app import create_route
from app import update_route
from app import delete_route
from app import users
from app import role_required
from app import user_trail