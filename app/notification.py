
from flask import redirect, url_for, flash, session
from app import app
import psycopg

@app.route('/notification', methods=['GET'])

def create_notification(user_id, message, status='unread'):
    """
    Создаёт уведомление для пользователя.
    """
    try:
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
                    INSERT INTO notifications (message, created_at, user_id, status)
                    VALUES (%s, CURRENT_TIMESTAMP, %s, %s)
                    ''',
                    (message, user_id, status)
                )
                con.commit()
                app.logger.info(f"Уведомление создано для пользователя {user_id}: {message}")
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при создании уведомления: {e}")

def notify_status_change(flight_id, new_status):
    """
    Уведомляет всех пользователей об изменении статуса рейса, включая дату и время отправления.
    """
    try:
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Получение данных рейса
                cur.execute(
                    '''
                    SELECT r.route_name, f.departure_date, f.dispatch_time
                    FROM flights f
                    JOIN routes r ON f.route_id = r.id
                    WHERE f.id = %s
                    ''',
                    (flight_id,)
                )
                flight_data = cur.fetchone()
                if not flight_data:
                    app.logger.error(f"Рейс с ID {flight_id} не найден.")
                    return

                route_name, departure_date, dispatch_time = flight_data

                # Получение подписчиков
                cur.execute(
                    '''
                    SELECT DISTINCT p.id
                    FROM p_user p
                    JOIN passenger_preferences pp ON pp.user_id = p.id
                    WHERE pp.preferred_route_id = (
                        SELECT route_id FROM flights WHERE id = %s
                    )
                    AND p.receive_notifications = TRUE
                    ''',
                    (flight_id,)
                )
                users = cur.fetchall()

                if not users:
                    app.logger.info(f"Нет подписчиков для рейса #{flight_id}. Уведомления не созданы.")
                    return

                # Создание уведомлений
                for user in users:
                    user_id = user[0]
                    message = (
                        f"Статус рейса (#ID: {flight_id}) по маршруту '{route_name}' "
                        f"(Дата: {departure_date}, Время: {dispatch_time}) изменился на '{new_status}'."
                    )
                    create_notification(user_id, message)
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при отправке уведомлений об изменении статуса: {e}")

def notify_cost_change(flight_id, old_cost, new_cost):
    """
    Уведомляет пользователей об изменении стоимости рейса.
    """
    try:
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Получение названия маршрута
                cur.execute(
                    '''
                    SELECT r.route_name
                    FROM routes r
                    JOIN flights f ON f.route_id = r.id
                    WHERE f.id = %s
                    ''',
                    (flight_id,)
                )
                route_name = cur.fetchone()[0]

                # Уведомление подписчиков
                cur.execute(
                    '''
                    SELECT DISTINCT p.id
                    FROM p_user p
                    JOIN passenger_preferences pp ON pp.user_id = p.id
                    WHERE pp.preferred_route_id = (
                        SELECT route_id FROM flights WHERE id = %s
                    )
                    AND p.receive_notifications = TRUE
                    ''',
                    (flight_id,)
                )
                users = cur.fetchall()

                for user in users:
                    user_id = user[0]
                    message = f"Стоимость рейса #{flight_id} по маршруту '{route_name}' была изменена с {old_cost} руб. на {new_cost} руб."
                    create_notification(user_id, message)
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при отправке уведомлений об изменении стоимости: {e}")

def notify_bus_change(flight_id, old_state_number, new_state_number):
    """
    Уведомляет пользователей об изменении номера автобуса.
    """
    try:
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Получение названия маршрута
                cur.execute(
                    '''
                    SELECT r.route_name
                    FROM routes r
                    JOIN flights f ON f.route_id = r.id
                    WHERE f.id = %s
                    ''',
                    (flight_id,)
                )
                route_name = cur.fetchone()[0]

                # Уведомление подписчиков
                cur.execute(
                    '''
                    SELECT DISTINCT p.id
                    FROM p_user p
                    JOIN passenger_preferences pp ON pp.user_id = p.id
                    WHERE pp.preferred_route_id = (
                        SELECT route_id FROM flights WHERE id = %s
                    )
                    AND p.receive_notifications = TRUE
                    ''',
                    (flight_id,)
                )
                users = cur.fetchall()

                for user in users:
                    user_id = user[0]
                    message = f"Гос.Номер автобуса рейса #{flight_id} по маршруту '{route_name}' был изменён с '{old_state_number}' на '{new_state_number}'."
                    create_notification(user_id, message)
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при отправке уведомлений об изменении номера автобуса: {e}")

@app.route('/delete_all_notifications', methods=['POST'])
def delete_all_notifications():
    """
    Удаляет все уведомления текущего пользователя из базы данных.
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Пользователь не аутентифицирован.', 'danger')
            return redirect(url_for('profile'))

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
                    DELETE FROM notifications
                    WHERE user_id = %s
                    ''',
                    (user_id,)
                )
                con.commit()

        flash('Все уведомления успешно удалены.', 'success')
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных при удалении уведомлений: {e}")
        flash('Ошибка при удалении уведомлений.', 'danger')

    return redirect(url_for('profile'))
