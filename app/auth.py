from functools import wraps
from flask import session, redirect, url_for

def registration_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('registered'):
            return redirect(url_for('login'))  # Перенаправление на страницу входа
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            user_roles = session.get('roles', [])
            if required_role not in user_roles:
                return redirect(url_for('index'))  # или отправить на страницу ошибки
            return f(*args, **kwargs)
        return wrapped_function
    return decorator
