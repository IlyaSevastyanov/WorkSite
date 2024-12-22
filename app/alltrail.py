
from flask import render_template
from app import app
import psycopg

from app.auth import registration_required


@app.route('/alltrail', methods=['GET'])
@registration_required
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
                # Получение списка всех маршрутов
                cur.execute("SELECT id, route_name FROM routes")
                all_routes = cur.fetchall()

        return render_template('alltrail.html', all_routes=all_routes)

    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        return render_template('error.html', message="Ошибка при загрузке маршрутов.")
