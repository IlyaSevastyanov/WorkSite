from flask import request, redirect, url_for, flash, session
from app import app
import psycopg
from app.auth import registration_required
@app.route('/update_route/<int:route_id>', methods=['POST'])
@registration_required
def update_route(route_id):
    try:
        # Извлечение данных из формы
        route_name = request.form.get('route_name').strip()
        travel_time = request.form.get('travel_time').strip()
        cost = request.form.get('cost').strip()

        # Логирование для отладки
        app.logger.info(f"Обновление маршрута {route_id} с названием {route_name}")

        # Проверка корректности данных
        if not route_name or not travel_time or not cost:
            flash('Все поля обязательны для заполнения.', 'danger')
            return redirect(url_for('alltrail'))

        if not cost.isdigit():
            flash('Стоимость должна быть числом.', 'danger')
            return redirect(url_for('alltrail'))

        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Проверка существования маршрута
                cur.execute(
                    '''
                    SELECT id FROM routes WHERE id = %s
                    ''',
                    (route_id,)
                )
                existing_route = cur.fetchone()

                if not existing_route:
                    flash('Маршрут не найден.', 'danger')
                    return redirect(url_for('alltrail'))

                # Обновление маршрута
                cur.execute(
                    '''
                    UPDATE routes
                    SET route_name = %s, travel_time = %s::INTERVAL, cost = %s
                    WHERE id = %s
                    ''',
                    (route_name, travel_time, cost, route_id)
                )

                con.commit()

        flash('Маршрут и связанные рейсы успешно обновлены.', 'success')
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при обновлении маршрута: {e}")
        flash('Ошибка при обновлении маршрута.', 'danger')

    return redirect(url_for('alltrail'))
