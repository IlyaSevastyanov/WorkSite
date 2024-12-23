from flask import session, render_template, flash, redirect, url_for, request
from werkzeug.security import check_password_hash
from app import app
import psycopg
from app.forms import LoginForm

@app.route('/login', methods=['GET', 'POST'])

def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            with psycopg.connect(
                    host=app.config['DB_SERVER'],
                    user=app.config['DB_USER'],
                    port=app.config['DB_PORT'],
                    password=app.config['DB_PASSWORD'],
                    dbname=app.config['DB_NAME']
            ) as con:
                with con.cursor() as cur:
                    # Логирование введённых данных
                    app.logger.info(f"Form data: email={form.email.data}")

                    # Получение пользователя по email
                    cur.execute(
                        '''
                        SELECT u.id, u.password, r.name AS role_name
                        FROM p_user u
                        LEFT JOIN user_role ur ON u.id = ur.user_id
                        LEFT JOIN p_role r ON ur.role_id = r.id
                        WHERE u.e_mail = %s
                        ''',
                        (form.email.data,)
                    )
                    user = cur.fetchone()

                    # Логирование данных из базы
                    app.logger.info(f"User fetched from DB: {user}")

                    if not user:
                        flash('Пользователь не найден. Зарегистрируйтесь.', 'warning')
                        return redirect(url_for('register'))

                    if not check_password_hash(user[1], form.password.data):
                        app.logger.info("Password mismatch")
                        flash('Неправильный email или пароль.', 'danger')
                        return render_template('login.html', form=form)

                    # Установка данных в сессии
                    session['registered'] = True
                    session['user_id'] = user[0]
                    session['user_role'] = user[2] if user[2] else "Пользователь"

                    # Лог успешного входа
                    app.logger.info(f"User logged in: id={user[0]}, role={session['user_role']}")
        except psycopg.Error as e:
            app.logger.error(f"Ошибка базы данных: {e}")
            flash('Ошибка при входе. Попробуйте позже.', 'danger')
            return render_template('login.html', form=form)

        flash(f'Вы успешно вошли в систему как {session["user_role"]}!', 'success')
        return redirect(url_for('index'))

    # Логирование ошибок валидации
    app.logger.info(f"Validation failed: {form.errors}")
    return render_template('login.html', form=form)
