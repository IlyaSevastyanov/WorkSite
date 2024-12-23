from flask import session, flash

from app import app
@app.before_request
def handle_flash_messages():
    if 'flash_message' in session:
        flash_message = session.pop('flash_message')  # Удаляем сообщение после обработки
        flash(flash_message['message'], flash_message['category'])

# Этот файл содержит запуск приложения
if __name__ == '__main__':
    app.run(debug=True)