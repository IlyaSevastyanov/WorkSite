from app import app
import psycopg
from flask import request, session, redirect, url_for, flash
from app.auth import registration_required

@app.route('/update_profile', methods=['POST'])
@registration_required  # Проверяем, что пользователь авторизован
def update_profile():
    try:
        # Извлечение данных из формы
        city = request.form.get('city', '').strip()  # Город
        phone_number = request.form.get('phone_number', '').strip()  # Номер телефона
        first_name = request.form.get('first_name', '').strip()  # Имя
        surname = request.form.get('surname', '').strip()  # Фамилия
        email = request.form.get('email', '').strip()  # Email
        receive_notifications = request.form.get('receive_notifications') == 'on'  # Чекбокс уведомлений

        # Проверка корректности данных
        if len(city) > 50:  # Проверяем длину строки города
            flash('Название города не должно превышать 50 символов.', 'danger')
            return redirect(url_for('profile'))

        if not phone_number.isdigit() or len(phone_number) > 15:  # Проверяем номер телефона
            flash('Номер телефона должен содержать только цифры и быть не длиннее 15 символов.', 'danger')
            return redirect(url_for('profile'))

        # Подключение к базе данных для обновления профиля
        with psycopg.connect(
                host=app.config['DB_SERVER'],  # Сервер базы данных
                user=app.config['DB_USER'],  # Имя пользователя базы данных
                port=app.config['DB_PORT'],  # Порт базы данных
                password=app.config['DB_PASSWORD'],  # Пароль для базы данных
                dbname=app.config['DB_NAME']  # Имя базы данных
        ) as con:
            with con.cursor() as cur:
                # Обновление данных пользователя
                cur.execute(
                    '''
                    UPDATE p_user
                    SET city = %s, phone_number = %s, first_name = %s, surname = %s, e_mail = %s, receive_notifications = %s
                    WHERE id = %s
                    ''',
                    (city, phone_number, first_name, surname, email, receive_notifications, session['user_id'])
                )
                con.commit()  # Сохранение изменений в базе данных

        # Сообщение об успешном обновлении профиля
        flash('Данные профиля успешно обновлены.', 'success')
        return redirect(url_for('profile'))
    except psycopg.Error as e:
        # Логирование ошибки базы данных и сообщение пользователю
        app.logger.error(f"Ошибка базы данных: {e}")
        flash('Ошибка при обновлении данных. Попробуйте позже.', 'danger')
        return redirect(url_for('profile'))
