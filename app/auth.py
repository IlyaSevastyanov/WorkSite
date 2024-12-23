from functools import wraps
from flask import session, redirect, url_for

# Проверяет, зарегистрирован ли пользователь
def registration_required(f):
    @wraps(f)  # Сохраняет метаданные оригинальной функции (например, имя, документацию)
    def decorated_function(*args, **kwargs):
        if not session.get('registered'):  # Проверка ключа 'registered' в сессии
            return redirect(url_for('login'))  # Перенаправление на страницу входа, если пользователь не зарегистрирован
        return f(*args, **kwargs)  # Если проверка пройдена, выполняется оригинальная функция
    return decorated_function
# Проверяет, имеет ли пользователь требуемую роль
def role_required(required_role):  # Принимает необходимую роль в качестве аргумента
    def decorator(f):
        @wraps(f)  # Сохраняет метаданные оригинальной функции
        def wrapped_function(*args, **kwargs):
            user_roles = session.get('roles', [])  # Получает список ролей пользователя из сессии
            if required_role not in user_roles:  # Проверяет, есть ли требуемая роль у пользователя
                return redirect(url_for('index'))  # Перенаправление на главную страницу или другую
            return f(*args, **kwargs)  # Если проверка пройдена, выполняется оригинальная функция
        return wrapped_function
    return decorator
