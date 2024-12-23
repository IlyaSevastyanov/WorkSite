from flask import session, flash
from app import app

@app.before_request
def handle_flash_messages():
    """
    Обрабатывает флеш-сообщения, которые были добавлены в сессию.
    Если сообщение присутствует, оно извлекается и передаётся во флеш-очередь для отображения.
    """
    if 'flash_message' in session:  # Проверяем наличие флеш-сообщения в сессии
        flash_message = session.pop('flash_message')  # Удаляем сообщение после извлечения
        # Добавляем сообщение во флеш для отображения в шаблоне
        flash(flash_message['message'], flash_message['category'])
