from flask import request
from app import app
from flask import render_template

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', title='Главная', text='Hello, World! (GET-запрос)')
    elif request.method == 'POST':
        return 'Hello, World! (POST-запрос)'
    else:
        return 'Неизвестный метод запроса'



