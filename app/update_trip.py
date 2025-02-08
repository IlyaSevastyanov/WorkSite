from flask import request, session, redirect, url_for, flash
import psycopg
from app import app
from app.auth import registration_required

@app.route('/update_trip', methods=['POST'])
@registration_required
def update_trip():
    try:
        route_id = request.form['route_id']  # ID маршрута
        flight_id = request.form['flight_id']  # ID рейса

        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Получение данных рейса для проверки
                cur.execute(
                    '''
                    SELECT f.departure_date, f.dispatch_time
                    FROM flights f
                    WHERE f.id = %s
                    ''',
                    (flight_id,)
                )
                flight_data = cur.fetchone()

                if not flight_data:
                    session['flash_message'] = {'message': 'Выбранный рейс не найден.', 'category': 'danger'}
                    return redirect(url_for('profile'))

                departure_date, dispatch_time = flight_data

                # Проверка на существующую запись
                cur.execute(
                    '''
                    SELECT th.id
                    FROM trip_history th
                    JOIN flights f ON th.flight_id = f.id
                    JOIN routes r ON f.route_id = r.id
                    WHERE th.user_id = %s 
                      AND f.id = %s 
                      AND r.id = %s 
                      AND f.departure_date = %s 
                      AND f.dispatch_time = %s
                    ''',
                    (session['user_id'], flight_id, route_id, departure_date, dispatch_time)
                )
                existing_trip = cur.fetchone()

                if existing_trip:
                    session['flash_message'] = {'message': 'Такая поездка уже существует.', 'category': 'info'}
                    return redirect(url_for('profile'))

                # Добавление новой поездки
                cur.execute(
                    '''
                    INSERT INTO trip_history (created_at, flight_id, user_id)
                    VALUES (CURRENT_TIMESTAMP, %s, %s)
                    ''',
                    (flight_id, session['user_id'])
                )
                con.commit()

                # Успешное добавление
                session['flash_message'] = {'message': 'Поездка успешно добавлена.', 'category': 'success'}
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        session['flash_message'] = {'message': 'Ошибка при добавлении поездки.', 'category': 'danger'}

    return redirect(url_for('profile'))

@app.route('/delete_trip/<int:trip_id>', methods=['POST'])
@registration_required
def delete_trip(trip_id):
    try:
        current_user_id = session['user_id']
        app.logger.info("Попытка удаления поездки: trip_id=%s, user_id=%s", trip_id, current_user_id)

        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Удаление записи из базы по id
                cur.execute(
                    '''
                    DELETE FROM trip_history
                    WHERE id = %s AND user_id = %s
                    ''',
                    (trip_id, current_user_id)
                )
                deleted_count = cur.rowcount  # Проверяем, сколько строк было удалено

                if deleted_count == 0:
                    app.logger.warning("Удаление не выполнено. Запись не найдена: trip_id=%s, user_id=%s", trip_id, current_user_id)
                    flash('Не удалось найти поездку для удаления.', 'danger')
                else:
                    con.commit()
                    app.logger.info("Удаление выполнено успешно: trip_id=%s, user_id=%s", trip_id, current_user_id)
                    flash('Поездка успешно удалена.', 'success')

    except psycopg.Error as e:
        app.logger.error("Ошибка базы данных при удалении поездки: %s", e)
        flash('Ошибка при удалении поездки.', 'danger')

    return redirect(url_for('profile'))
