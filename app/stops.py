
from flask import render_template
from app import app
import psycopg

from app.auth import registration_required


@app.route('/stops')
@registration_required
def stops():
    try:
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            cur = con.cursor()
            stops_data = cur.execute(
                'SELECT name, address, route_name FROM bus_stops'
            ).fetchall()
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        return render_template('error.html', message="Ошибка при подключении к базе данных.")

    return render_template(
        'stops.html',
        title='Список остановок',
        stops=stops_data
    )