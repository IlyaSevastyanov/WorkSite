from app import app
import psycopg
from flask import render_template, flash, redirect, url_for, session
from app.forms import RegistrationForm
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
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
                    # Проверка уникальности email
                    cur.execute('SELECT id FROM p_user WHERE e_mail = %s', (form.email.data,))
                    if cur.fetchone():
                        flash('Пользователь с таким email уже существует.', 'danger')
                        return render_template('registration.html', form=form)

                    # Проверка уникальности пароля
                    cur.execute('SELECT id FROM p_user WHERE password = crypt(%s, password)', (form.password.data,))
                    if cur.fetchone():
                        flash('Пользователь с таким паролем уже существует.', 'danger')
                        return render_template('registration.html', form=form)

                    # Добавление нового пользователя
                    cur.execute(
                        '''
                        INSERT INTO p_user (e_mail, password, first_name, surname, phone_number)
                        VALUES (%s, crypt(%s, gen_salt('bf')), %s, %s, %s)
                        ''',
                        (
                            form.email.data,
                            form.password.data,
                            form.first_name.data,
                            form.surname.data,
                            form.phone_number.data
                        )
                    )
                    con.commit()

        except psycopg.Error as e:
            app.logger.error(f"Ошибка базы данных: {e}")
            flash('Ошибка при регистрации. Попробуйте позже.', 'danger')
            return render_template('registration.html', form=form)

        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))

    return render_template('registration.html', form=form)
