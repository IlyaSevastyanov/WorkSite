
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
                        SELECT id
                        FROM p_user
                        WHERE e_mail = %s AND password = crypt(%s, password)
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

        except psycopg.Error as e:
            app.logger.error(f"Ошибка базы данных: {e}")
            flash('Ошибка при входе. Попробуйте позже.', 'danger')
            return render_template('login.html', form=form)

        flash('Вы успешно вошли в систему!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html', form=form)
