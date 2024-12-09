from flask import request, render_template
from app import app
import psycopg

from flask import request, render_template
from app import app
import psycopg


@app.route('/flights', methods=['GET'])
def flights():
    # Получение параметров фильтра
    route_id = request.args.get('route_id')
    departure_date = request.args.get('departure_date')

    try:
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            cur = con.cursor()

            # Если дата не указана, выбираем минимальную доступную дату
            if not departure_date:
                cur.execute('''
                    SELECT MIN(departure_date)
                    FROM flights
                    WHERE departure_date >= CURRENT_DATE
                ''')
                departure_date = cur.fetchone()[0]

                # Если нет доступных дат, возвращаем сообщение об отсутствии рейсов
                if not departure_date:
                    return render_template(
                        'flights.html',
                        title='Список рейсов',
                        flights=[],
                        selected_date=None,
                        message="На ближайшие даты рейсов нет."
                    )

            # Формирование SQL-запроса с фильтрацией
            query = '''
                SELECT route_id, departure_date, dispatch_time, flight_status
                FROM flights
                WHERE (%s::integer IS NULL OR route_id = %s::integer)
                  AND (%s::date IS NULL OR departure_date = %s::date)
            '''
            cur.execute(query, (route_id, route_id, departure_date, departure_date))
            flights_data = cur.fetchall()

            # Если данных по запросу нет
            if not flights_data:
                return render_template(
                    'flights.html',
                    title='Список рейсов',
                    flights=[],
                    selected_date=departure_date,
                    message="На выбранную дату рейсов нет."
                )

    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        return render_template('error.html', message="Ошибка при подключении к базе данных.")

    return render_template(
        'flights.html',
        title='Список рейсов',
        flights=flights_data,
        selected_date=departure_date,
        message=None
    )


