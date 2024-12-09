
from flask import render_template
from app import app
import psycopg


@app.route('/buses')
def buses():
    try:
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            cur = con.cursor()
            buses_data = cur.execute(
                'SELECT state_number, model, brand, capacity FROM buses'
            ).fetchall()
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        return render_template('error.html', message="Ошибка при подключении к базе данных.")

    return render_template(
        'buses.html',
        title='Список автобусов',
        buses=buses_data
    )
