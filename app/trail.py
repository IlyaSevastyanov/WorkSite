from flask import render_template, session
from app import app
import psycopg
from app.auth import registration_required

@app.route('/trail', methods=['GET'])
@registration_required
def trail():
    try:
        with psycopg.connect(
            host=app.config['DB_SERVER'],
            user=app.config['DB_USER'],
            port=app.config['DB_PORT'],
            password=app.config['DB_PASSWORD'],
            dbname=app.config['DB_NAME']
        ) as con:
            cur = con.cursor()

            # Получение всех маршрутов
            cur.execute("SELECT id, route_name FROM routes")
            all_routes = [{'id': row[0], 'route_name': row[1]} for row in cur.fetchall()]

            # Получение предпочтений пользователя
            cur.execute(
                """
                SELECT preferred_route_id 
                FROM passenger_preferences 
                WHERE user_id = %s
                """,
                (session['user_id'],)
            )
            preferred_routes = [row[0] for row in cur.fetchall()]

    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        return render_template('error.html', message="Ошибка при подключении к базе данных.")

    return render_template(
        'trail.html',
        all_routes=all_routes,
        preferred_routes=preferred_routes
    )
