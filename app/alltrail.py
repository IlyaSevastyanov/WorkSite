from flask import render_template, session, flash
from app import app
import psycopg

from app.auth import registration_required
from app.role_required import role_required


@app.route('/alltrail', methods=['GET'])
@registration_required
@role_required('Администратор')
def alltrail():
    try:

        with psycopg.connect(
            host=app.config['DB_SERVER'],
            user=app.config['DB_USER'],
            port=app.config['DB_PORT'],
            password=app.config['DB_PASSWORD'],
            dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Получение списка маршрутов с доп. данными
                cur.execute(
                    '''
                    SELECT 
                        r.id, 
                        r.route_name, 
                        r.travel_time, 
                        r.cost, 
                        r.state_number
                    FROM routes r
                    '''
                )
                all_routes = cur.fetchall()
                # Получение списка всех автобусов
                cur.execute("SELECT id, state_number FROM buses")
                all_buses = cur.fetchall()

                # Получение списка всех остановок
                cur.execute("SELECT id, name, route_id, route_name FROM bus_stops")
                all_stops = cur.fetchall()
        return render_template(
            'alltrail.html',
            all_routes=all_routes,
            all_buses=all_buses,
            all_stops=all_stops  # Передача списка остановок
        )
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        return render_template('error.html', message="Ошибка при загрузке маршрутов.")
