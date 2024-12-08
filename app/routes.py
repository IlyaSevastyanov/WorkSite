from flask import request, render_template
from app import app
import psycopg

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', title='Главная', text='Hello, World! (GET-запрос)')
    elif request.method == 'POST':
        return 'Hello, World! (POST-запрос)'
    else:
        return 'Неизвестный метод запроса'


@app.route('/flights')
def flights():
    flight_status_filter = request.args.get('status')  # Параметр фильтрации из URL
    try:
        with psycopg.connect(
            host=app.config['DB_SERVER'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            dbname=app.config['DB_NAME']
        ) as con:
            cur = con.cursor()
            if flight_status_filter:
                cur.execute(
                    'SELECT route_name, departure_date, dispatch_time, flight_status '
                    'FROM flights WHERE flight_status = %s', (flight_status_filter,)
                )
            else:
                cur.execute(
                    'SELECT route_name, departure_date, dispatch_time, flight_status '
                    'FROM flights'
                )
            flights_data = cur.fetchall()
    except Exception as e:
        return f"Ошибка при подключении к базе данных: {e}"

    return render_template(
        'flights.html',
        title='Список рейсов',
        flights=flights_data,
        flight_status_filter=flight_status_filter
    )
