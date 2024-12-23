from flask import render_template, session, flash
from app import app
import psycopg

from app.auth import registration_required
from app.role_required import role_required


@app.route('/alltrail', methods=['GET'])
@registration_required  # Проверяет, зарегистрирован ли пользователь
@role_required('Администратор')  # Проверяет, является ли пользователь администратором
def alltrail():
    try:

        with psycopg.connect(
                host=app.config['DB_SERVER'],  # Подключение к серверу базы данных
                user=app.config['DB_USER'],  # Имя пользователя базы данных
                port=app.config['DB_PORT'],  # Порт подключения к базе данных
                password=app.config['DB_PASSWORD'],  # Пароль для подключения
                dbname=app.config['DB_NAME']  # Имя базы данных
        ) as con:
            with con.cursor() as cur:
                # Получение списка маршрутов с дополнительными данными
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
                all_routes = cur.fetchall()  # Сохраняем результат запроса к маршрутам

                # Получение списка всех автобусов
                cur.execute("SELECT id, state_number FROM buses")
                all_buses = cur.fetchall()  # Сохраняем результат запроса к автобусам

                # Получение списка всех остановок
                cur.execute("SELECT id, name, route_id, route_name FROM bus_stops")
                all_stops = cur.fetchall()  # Сохраняем результат запроса к остановкам

        # Передача данных в шаблон для отображения
        return render_template(
            'alltrail.html',
            all_routes=all_routes,  # Передача списка маршрутов в шаблон
            all_buses=all_buses,  # Передача списка автобусов в шаблон
            all_stops=all_stops  # Передача списка остановок в шаблон
        )
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")  # Логирование ошибок базы данных
        return render_template('error.html', message="Ошибка при загрузке маршрутов.")  # Отображение страницы ошибки
