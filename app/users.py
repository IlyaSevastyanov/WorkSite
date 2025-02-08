from flask import render_template, request, redirect, url_for, flash
from app import app
import psycopg
from app.auth import registration_required
from app.role_required import role_required


@app.route('/users', methods=['GET'])
@registration_required
@role_required('Администратор')
def users():
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
                    SELECT 
                        u.id AS user_id, 
                        u.first_name, 
                        u.surname, 
                        u.e_mail, 
                        u.phone_number, 
                        r.name AS role_name
                    FROM p_user u
                    LEFT JOIN user_role ur ON u.id = ur.user_id
                    LEFT JOIN p_role r ON ur.role_id = r.id
                    ORDER BY u.first_name, u.surname;
                    '''
                )
                users = cur.fetchall()

        return render_template('users.html', users=users)

    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        return render_template('error.html', message="Ошибка при загрузке пользователей.")


@app.route('/update_user_role', methods=['POST'])
@registration_required
@role_required('Администратор')
def update_user_role():
    user_id = request.form.get('user_id')
    role_id = request.form.get('role_id')

    try:
        with psycopg.connect(
                host=app.config['DB_SERVER'],
                user=app.config['DB_USER'],
                port=app.config['DB_PORT'],
                password=app.config['DB_PASSWORD'],
                dbname=app.config['DB_NAME']
        ) as con:
            with con.cursor() as cur:
                # Удаляем старую роль
                cur.execute('DELETE FROM user_role WHERE user_id = %s', (user_id,))

                # Добавляем новую роль
                cur.execute('INSERT INTO user_role (user_id, role_id) VALUES (%s, %s)', (user_id, role_id))
                con.commit()

        flash('Роль пользователя успешно обновлена.', 'success')
    except psycopg.Error as e:
        app.logger.error(f"Ошибка базы данных: {e}")
        flash('Ошибка при обновлении роли пользователя.', 'danger')
    return redirect(url_for('users'))
