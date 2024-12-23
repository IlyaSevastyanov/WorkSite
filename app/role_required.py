from functools import wraps
from flask import session, redirect, url_for, flash

def role_required(required_role):
    """
    Декоратор для ограничения доступа к маршруту в зависимости от роли пользователя.

    Аргументы:
    - required_role (str): Роль, которая необходима для доступа к маршруту (например, 'Администратор').

    Возвращает:
    - Функцию-обёртку, которая проверяет роль пользователя перед выполнением оригинальной функции.
    """
    def decorator(func):
        @wraps(func)  # Сохраняет метаданные оригинальной функции (например, имя, документацию)
        def wrapper(*args, **kwargs):
            """
            *args и **kwargs позволяют обёртке принимать любое количество позиционных и именованных аргументов,
            которые затем передаются в оригинальную функцию.

            *args:
            - Переменное количество позиционных аргументов, переданных в оборачиваемую функцию.

            **kwargs:
            - Переменное количество именованных аргументов, переданных в оборачиваемую функцию.

            Это полезно для сохранения универсальности декоратора, чтобы он мог работать с функциями
            любой сигнатуры (количества и типа аргументов).
            """
            # Проверка: есть ли роль в сессии
            if 'user_role' not in session:
                flash('Вы должны войти в систему.', 'danger')  # Показываем сообщение об ошибке
                return redirect(url_for('login'))  # Перенаправляем на страницу входа

            # Проверка: соответствует ли роль пользователя требуемой
            if session['user_role'] != required_role:
                flash('У вас нет доступа к этой странице.', 'danger')  # Показываем сообщение об ошибке
                return redirect(url_for('index'))  # Перенаправляем на главную страницу

            # Если все проверки пройдены, выполняем оригинальную функцию
            return func(*args, **kwargs)
        return wrapper
    return decorator
