from collections import defaultdict

from flask import render_template
from app import app
import psycopg

@app.route('/flights')
def flights():
    try:
        print("Подключение к базе данных...")
        # Создаем соединение с базой данных
        with psycopg.connect(
            host=app.config['DB_SERVER'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            dbname=app.config['DB_NAME']
        ) as con:
            print("Соединение установлено.")
            cur = con.cursor()

            # Упрощенный запрос без фильтрации
            flights_data = cur.execute(
                'SELECT route_id, departure_date, dispatch_time, flight_status FROM flights ').fetchall()
            grouped = defaultdict(list)
            for i in range(len(flights_data)):
                key = (flights_data[i][0], flights_data[i][1])
                grouped[key].append(flights_data[i][2])

    except Exception as e:
        print(f"Ошибка при подключении или выполнении запроса: {e}")
        return f"Ошибка при подключении к базе данных: {e}"

    # Возвращаем данные в шаблон
    return render_template(
        'flights.html',
        title='Список рейсов',
        flights=flights_data
    )
