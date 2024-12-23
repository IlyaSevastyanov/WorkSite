from functools import wraps
from flask import session, redirect, url_for, flash

def role_required(required_role):
    """
    Декоратор для ограничения доступа к маршруту в зависимости от роли пользователя.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_role' not in session:
                flash('Вы должны войти в систему.', 'danger')
                return redirect(url_for('login'))

            if session['user_role'] != required_role:
                flash('У вас нет доступа к этой странице.', 'danger')
                return redirect(url_for('index'))  # Перенаправление на главную страницу или другую
            return func(*args, **kwargs)
        return wrapper
    return decorator
