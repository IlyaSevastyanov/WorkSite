
from flask import render_template, jsonify
from app import app
import psycopg

from app.auth import registration_required


@app.route('/buses')
@registration_required
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
@app.route('/get_bus_state_number/<int:bus_id>', methods=['GET'])
@registration_required
def get_bus_state_number(bus_id):
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
                    SELECT state_number
                    FROM buses
                    WHERE id = %s
                    ''',
                    (bus_id,)
                )
                result = cur.fetchone()
                return jsonify({'state_number': result[0] if result else ''})
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при получении госномера автобуса: {e}")
        return jsonify({'state_number': ''}), 500
