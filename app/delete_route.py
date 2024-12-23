from flask import request, redirect, url_for, flash, session
from app import app
import psycopg
from app.auth import registration_required
@app.route('/delete_route/<int:route_id>', methods=['POST'])
@registration_required
def delete_route(route_id):
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
                    DELETE FROM routes
                    WHERE id = %s
                    ''',
                    (route_id,)
                )
                con.commit()
        flash('Маршрут успешно удалён.', 'success')
    except psycopg.Error as e:
        app.logger.error(f"Ошибка при удалении маршрута: {e}")
        flash('Ошибка при удалении маршрута.', 'danger')
    return redirect(url_for('alltrail'))
