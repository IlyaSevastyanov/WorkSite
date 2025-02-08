from app import app
import psycopg
from flask import request, redirect, url_for, flash
from app.auth import registration_required
@app.route('/create_route', methods=['POST'])
@registration_required
def create_route():
    route_name = request.form.get('route_name').strip()
    travel_time = request.form.get('travel_time').strip()
    cost = request.form.get('cost').strip()
    bus_id = request.form.get('bus_id').strip()
    selected_stops = request.form.getlist('stops')  # Получение списка выбранных остановок

    try:
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Получение данных существующего автобуса
                cur.execute(
                    '''
                    SELECT state_number, model, brand, capacity
                    FROM buses
                    WHERE id = %s
                    ''',
                    (bus_id,)
                )
                bus_data = cur.fetchone()
                if not bus_data:
                    flash(f"Автобус с ID {bus_id} не найден.", "danger")
                    return redirect(url_for('alltrail'))

                state_number = bus_data[0]  # Госномер автобуса

                # Создание новой записи автобуса с новым ID
                cur.execute(
                    '''
                    INSERT INTO buses (state_number, model, brand, capacity)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    ''',
                    (bus_data[0], bus_data[1], bus_data[2], bus_data[3])
                )
                new_bus_id = cur.fetchone()[0]

                # Создание маршрута с новым bus_id и state_number
                cur.execute(
                    '''
                    INSERT INTO routes (route_name, travel_time, cost, bus_id, state_number)
                    VALUES (%s, %s::INTERVAL, %s, %s, %s)
                    RETURNING id
                    ''',
                    (route_name, travel_time, cost, new_bus_id, state_number)
                )
                new_route_id = cur.fetchone()[0]

                # Добавление выбранных остановок в bus_stops
                for stop_id in selected_stops:
                    # Получение имени и адреса остановки
                    cur.execute(
                        '''
                        SELECT name, address
                        FROM bus_stops
                        WHERE id = %s
                        ''',
                        (stop_id,)
                    )
                    stop_data = cur.fetchone()
                    if stop_data:
                        stop_name, stop_address = stop_data
                        cur.execute(
                            '''
                            INSERT INTO bus_stops (name, address, route_id, route_name)
                            VALUES (%s, %s, %s, %s)
                            ''',
                            (stop_name, stop_address, new_route_id, route_name)
                        )
                    else:
                        flash(f"Остановка с ID {stop_id} не найдена.", "danger")

                con.commit()

        flash('Маршрут, автобус и остановки успешно добавлены.', 'success')
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при создании маршрута и назначении остановок: {e}")
        flash('Ошибка при создании маршрута.', 'danger')
    return redirect(url_for('alltrail'))
