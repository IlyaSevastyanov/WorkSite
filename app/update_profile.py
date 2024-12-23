from app import app
import psycopg
from flask import request, session, redirect, url_for, flash
from app.auth import registration_required


@app.route('/update_profile', methods=['POST'])
@registration_required
def update_profile():
    try:
        city = request.form.get('city', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        first_name = request.form.get('first_name', '').strip()
        surname = request.form.get('surname', '').strip()
        email = request.form.get('email', '').strip()
        receive_notifications = request.form.get('receive_notifications') == 'on'  # Проверяем значение чекбокса

        # Проверка корректности данных
        if len(city) > 50:
            flash('Название города не должно превышать 50 символов.', 'danger')
            return redirect(url_for('profile'))

        if not phone_number.isdigit() or len(phone_number) > 15:
            flash('Номер телефона должен содержать только цифры и быть не длиннее 15 символов.', 'danger')
            return redirect(url_for('profile'))

        # Обновление данных в базе
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
                    UPDATE p_user
                    SET city = %s, phone_number = %s, first_name = %s, surname = %s, e_mail = %s, receive_notifications = %s
                    WHERE id = %s
                    ''',
                    (city, phone_number, first_name, surname, email, receive_notifications, session['user_id'])
                )
                con.commit()

        flash('Данные профиля успешно обновлены.', 'success')
        return redirect(url_for('profile'))
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        flash('Ошибка при обновлении данных. Попробуйте позже.', 'danger')
        return redirect(url_for('profile'))

