
from flask import request, render_template, jsonify
from app import app
import psycopg
from app.auth import registration_required


@app.route('/flights', methods=['GET'])
@registration_required
def flights():
    route_name = request.args.get('route_name')  # Название маршрута
    departure_date = request.args.get('departure_date')  # Дата отправления
    filter_type = request.args.get('filter')  # Тип фильтра: all_routes или by_date

    try:
        with psycopg.connect(
            host=app.config['DB_SERVER'],
            user=app.config['DB_USER'],
            port=app.config['DB_PORT'],
            password=app.config['DB_PASSWORD'],
            dbname=app.config['DB_NAME']
        ) as con:
            cur = con.cursor()

            # Извлечение списка всех маршрутов
            cur.execute("SELECT route_name FROM routes")
            routes = cur.fetchall()

            # Определяем базовый запрос и параметры
            query = '''
                SELECT f.id AS flight_id, r.route_name, f.departure_date, 
                       f.dispatch_time, f.flight_status
                FROM flights f
                JOIN routes r ON f.route_id = r.id
                WHERE (%s::TEXT IS NULL OR LOWER(r.route_name) = LOWER(%s::TEXT))
            '''
            parameters = [route_name.strip() if route_name else None, route_name.strip() if route_name else None]

            # Если фильтр — только по маршруту (все рейсы этого маршрута)
            if filter_type == "all_routes":
                query += '''
                    ORDER BY f.departure_date, f.dispatch_time;
                '''
            elif filter_type == "by_date":
                # Фильтр по маршруту и дате
                query += '''
                    AND (%s::DATE IS NULL OR f.departure_date = %s::DATE)
                    ORDER BY f.departure_date, f.dispatch_time;
                '''
                parameters.extend([departure_date if departure_date else None, departure_date if departure_date else None])

            cur.execute(query, parameters)
            flights_data = cur.fetchall()

            # Если данных по запросу нет
            if not flights_data:
                return render_template(
                    'flights.html',
                    title='Список рейсов',
                    flights=[],
                    selected_date=departure_date,
                    routes=routes,
                    message="На выбранную дату или маршрут данных нет."
                )

    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        return render_template('error.html', message="Ошибка при подключении к базе данных.")

    return render_template(
        'flights.html',
        title='Список рейсов',
        flights=flights_data,
        selected_date=departure_date,
        routes=routes,
        message=None
    )


@app.route('/get_flights/<int:route_id>', methods=['GET'])
@registration_required
def get_flights(route_id):
    try:
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Получение рейсов для выбранного маршрута
                cur.execute(
                    '''
                    SELECT 
                        f.id AS flight_id, 
                        f.departure_date, 
                        f.dispatch_time, 
                        b.state_number, 
                        b.model, 
                        b.capacity, 
                        r.cost
                    FROM flights f
                    JOIN routes r ON f.route_id = r.id
                    JOIN buses b ON r.bus_id = b.id
                    WHERE f.route_id = %s
                    ORDER BY f.departure_date, f.dispatch_time
                    ''',
                    (route_id,)
                )
                flights = [
                    {
                        'id': row[0],
                        'date': row[1].strftime('%Y-%m-%d'),
                        'time': row[2].strftime('%H:%M'),
                        'bus_number': row[3],
                        'bus_model': row[4],
                        'capacity': row[5],
                        'price': row[6]
                    }
                    for row in cur.fetchall()
                ]

        return jsonify({'flights': flights}), 200
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        return jsonify({'error': 'Ошибка при загрузке рейсов'}), 500
