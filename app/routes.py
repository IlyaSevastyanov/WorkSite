
from flask import render_template, session, redirect, url_for, flash
from app import app
from app.auth import registration_required


@app.route('/')
@registration_required
def index():
    return render_template('index.html', title='Главная страница')

