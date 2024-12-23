
from flask import session, render_template, flash, redirect, url_for
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
                    # Проверка email и пароля
                    cur.execute(
                        '''
                        SELECT u.id, r.name AS role_name
                        FROM p_user u
                        LEFT JOIN user_role ur ON u.id = ur.user_id
                        LEFT JOIN p_role r ON ur.role_id = r.id
                        WHERE u.e_mail = %s AND u.password = crypt(%s, u.password)
                        ''',
                        (form.email.data, form.password.data)
                    )
                    user = cur.fetchone()

                    if not user:
                        flash('Неправильный email или пароль.', 'danger')
                        return render_template('login.html', form=form)

                    # Установка данных в сессии
                    session['registered'] = True
                    session['user_id'] = user[0]
                    if user:
                        session['user_role'] = user[1]  # Пример: "Администратор" или "Пользователь"
                    else:
                        session['user_role'] = "Пользователь"  # По умолчанию
        except psycopg.Error as e:
            app.logger.error(f"Ошибка базы данных: {e}")
            flash('Ошибка при входе. Попробуйте позже.', 'danger')
            return render_template('login.html', form=form)

        flash(f'Вы успешно вошли в систему как {session["user_role"]}!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html', form=form)
