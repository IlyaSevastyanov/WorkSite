from flask import flash
from app import app
import psycopg
from flask import render_template, session
from app.auth import registration_required

@app.route('/profile', methods=['GET'])
@registration_required
def profile():
    try:
        # Проверка наличия flash-сообщения из сессии
        if 'flash_message' in session:
            flash_message = session.pop('flash_message')  # Удаляем сообщение после обработки
            flash(flash_message['message'], flash_message['category'])
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Основные данные пользователя
                cur.execute(
                    '''
                    SELECT first_name, surname, e_mail, phone_number, city 
                    FROM p_user 
                    WHERE id = %s
                    ''',
                    (session['user_id'],)
                )
                user_data = cur.fetchone()

                if not user_data:
                    flash('Пользователь не найден.', 'danger')
                    raise ValueError("Пользователь не найден")

                user = {
                    'first_name': user_data[0],
                    'surname': user_data[1],
                    'email': user_data[2],
                    'phone_number': user_data[3],
                    'city': user_data[4]
                }

                # Получение предпочитаемых маршрутов
                cur.execute(
                    '''
                    SELECT r.id, r.route_name
                    FROM passenger_preferences pp
                    JOIN routes r ON pp.preferred_route_id = r.id
                    WHERE pp.user_id = %s
                    ''',
                    (session['user_id'],)
                )
                preferred_routes = cur.fetchall()
                if not preferred_routes:
                 session['flash_message'] = {'message': 'Нет предпочитаемых маршрутов.', 'category': 'info'}
                # Получение ближайших рейсов для каждого маршрута
                nearest_flights = []
                for route_id, route_name in preferred_routes:
                    cur.execute(
                        '''
                        SELECT f.departure_date, f.dispatch_time, f.flight_status
                        FROM flights f
                        WHERE f.route_id = %s AND f.departure_date >= CURRENT_DATE
                        ORDER BY f.departure_date ASC, f.dispatch_time ASC
                        LIMIT 1
                        ''',
                        (route_id,)
                    )
                    flight = cur.fetchone()
                    nearest_flights.append({
                        'route_name': route_name,
                        'flight': flight  # None, если рейсов нет
                    })

                # История поездок
                cur.execute(
                    '''
SELECT 
    th.id,  -- ID записи из trip_history
    TO_CHAR(th.created_at, 'YYYY-MM-DD HH24:MI:SS') AS formatted_created_at,  -- Форматированная дата добавления
    r.route_name,            -- Название маршрута
    f.id AS flight_id,       -- ID рейса маршрута
    f.departure_date,        -- Дата рейса
    f.dispatch_time,         -- Время отправления рейса
    b.state_number,          -- Гос. номер автобуса
    b.model,                 -- Модель автобуса
    r.cost                   -- Стоимость рейса
FROM trip_history th
JOIN flights f ON th.flight_id = f.id
JOIN routes r ON f.route_id = r.id
JOIN buses b ON r.bus_id = b.id
WHERE th.user_id = %s
ORDER BY th.created_at DESC;


                    ''',
                    (session['user_id'],)
                )
                trip_history = cur.fetchall()

                # Список маршрутов для добавления поездки
                cur.execute("SELECT id, route_name FROM routes")
                all_routes = cur.fetchall()

        return render_template(
            'user.html',
            user=user,
            preferred_routes=preferred_routes,
            nearest_flights=nearest_flights,
            trip_history=trip_history,
            all_routes=all_routes
        )

    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        flash('Ошибка при загрузке данных профиля.', 'danger')
        return render_template('error.html', message="Ошибка при загрузке профиля.")
    except ValueError as e:
        app.logger.error(f"Ошибка: {e}")
        flash(str(e), 'danger')
        return render_template('error.html', message=str(e))
