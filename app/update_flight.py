from flask import flash, request, redirect, url_for
from app import app
import psycopg
from app.auth import registration_required
from app.notification import notify_cost_change
from app.notification import notify_bus_change
from app.notification import notify_status_change
@app.route('/update_flight_status/<int:flight_id>', methods=['POST'])
@registration_required
def update_flight_status(flight_id):
    try:
        new_status = request.form['status'].strip()

        # Проверка корректности статуса
        allowed_statuses = ['Отправлен', 'Задержан', 'Отменён']
        if new_status not in allowed_statuses:
            flash('Некорректный статус рейса.', 'danger')
            return redirect(url_for('flights'))

        # Обновление статуса
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                cur.execute(
                    '''
                    UPDATE flights
                    SET flight_status = %s
                    WHERE id = %s
                    ''',
                    (new_status, flight_id)
                )
                con.commit()
                notify_status_change(flight_id, new_status)
        flash('Статус рейса успешно обновлён.', 'success')
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при обновлении статуса рейса: {e}")
        flash('Ошибка при обновлении статуса рейса.', 'danger')
    return redirect(url_for('flights'))


@app.route('/update_flight_bus/<int:flight_id>', methods=['POST'])
@registration_required
def update_flight_bus(flight_id):
    try:
        import re
        new_state_number = request.form.get('state_number').strip()

        # Проверка корректности ввода
        if not new_state_number:
            flash('Номер автобуса не может быть пустым.', 'danger')
            return redirect(url_for('flights'))

        # Регулярное выражение для проверки формата
        state_number_regex = r'^[А-Я]{2}\d{3}[А-Я]{2}$'
        if not re.match(state_number_regex, new_state_number):
            flash('Номер автобуса должен быть в формате: AA123AA', 'danger')
            return redirect(url_for('flights'))

        if len(new_state_number) > 8:
            flash('Номер автобуса не должен превышать 8 символов.', 'danger')
            return redirect(url_for('flights'))

        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Получение текущего номера автобуса
                cur.execute(
                    '''
                    SELECT b.state_number
                    FROM buses b
                    JOIN routes r ON r.bus_id = b.id
                    JOIN flights f ON f.route_id = r.id
                    WHERE f.id = %s
                    ''',
                    (flight_id,)
                )
                old_state_number = cur.fetchone()[0]

                # Обновление гос номера автобуса
                cur.execute(
                    '''
                    UPDATE buses
                    SET state_number = %s
                    WHERE id = (
                        SELECT r.bus_id
                        FROM routes r
                        JOIN flights f ON f.route_id = r.id
                        WHERE f.id = %s
                    )
                    ''',
                    (new_state_number, flight_id)
                )
                con.commit()

        # Уведомление о изменении номера автобуса
        notify_bus_change(flight_id, old_state_number, new_state_number)

        flash('Номер автобуса успешно обновлён.', 'success')
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при обновлении номера автобуса: {e}")
        flash('Ошибка при обновлении номера автобуса.', 'danger')
    return redirect(url_for('flights'))


@app.route('/update_flight_cost/<int:flight_id>', methods=['POST'])
@registration_required
def update_flight_cost(flight_id):
    try:
        new_cost = request.form.get('cost')

        # Проверка корректности ввода
        if not new_cost or not new_cost.isdigit() or int(new_cost) <= 0:
            flash('Стоимость должна быть положительным числом.', 'danger')
            return redirect(url_for('flights'))

        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Получение текущей стоимости
                cur.execute(
                    '''
                    SELECT r.cost
                    FROM routes r
                    JOIN flights f ON f.route_id = r.id
                    WHERE f.id = %s
                    ''',
                    (flight_id,)
                )
                old_cost = cur.fetchone()[0]

                # Обновление стоимости
                cur.execute(
                    '''
                    UPDATE routes
                    SET cost = %s
                    WHERE id = (
                        SELECT route_id
                        FROM flights
                        WHERE id = %s
                    )
                    ''',
                    (new_cost, flight_id)
                )
                con.commit()

        # Уведомление о изменении стоимости
        notify_cost_change(flight_id, old_cost, new_cost)

        flash('Стоимость рейса успешно обновлена.', 'success')
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при обновлении стоимости рейса: {e}")
        flash('Ошибка при обновлении стоимости рейса.', 'danger')
    return redirect(url_for('flights'))

