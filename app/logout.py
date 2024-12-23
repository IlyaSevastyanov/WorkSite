from flask import session,  flash, redirect, url_for
from app import app

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы успешно вышли из аккаунта.', 'success')
    return redirect(url_for('register'))
