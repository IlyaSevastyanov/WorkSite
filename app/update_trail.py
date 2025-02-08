from flask import request, redirect, url_for, flash, session
from app import app
import psycopg
from app.auth import registration_required

@app.route('/update_trail', methods=['POST'])
@registration_required
def update_trail():
    try:
        # Получение выбранных маршрутов из формы
        selected_routes = request.form.getlist('preferred_routes[]')

        if not selected_routes:
            flash('Выберите хотя бы один маршрут перед сохранением.', 'danger')
            return redirect(url_for('trail'))

        with psycopg.connect(
            host=app.config['DB_SERVER'],
            user=app.config['DB_USER'],
            port=app.config['DB_PORT'],
            password=app.config['DB_PASSWORD'],
            dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Удаление старых предпочтений
                cur.execute("DELETE FROM passenger_preferences WHERE user_id = %s", (session['user_id'],))

                # Добавление новых предпочтений
                for route_id in selected_routes:
                    cur.execute(
                        """
                        INSERT INTO passenger_preferences (user_id, preferred_route_id)
                        VALUES (%s, %s)
                        """,
                        (session['user_id'], route_id)
                    )
                con.commit()

        flash('Предпочтения успешно обновлены.', 'success')
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        flash('Ошибка при обновлении предпочтений.', 'danger')

    return redirect(url_for('profile'))
