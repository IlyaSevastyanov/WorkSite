from flask import Flask
from flask_bootstrap5 import Bootstrap5
from app.config import Config

# Инициализация приложения Flask
app = Flask(__name__)

# Подключение Bootstrap для упрощённого создания интерфейса
bootstrap = Bootstrap5(app)

# Загрузка конфигурации приложения из объекта Config
app.config.from_object(Config)

# Импорт различных модулей приложения для маршрутов и логики
from app import routes  # Основные маршруты
from app import flights  # Маршруты и логика, связанные с рейсами
from app import buses  # Маршруты и логика, связанные с автобусами
from app import stops  # Логика обработки остановок
from app import trail  # Маршруты и логика, связанные с путями
from app import forms  # Формы для пользовательского ввода
from app import register  # Регистрация пользователей
from app import login  # Вход пользователей
from app import profile  # Профиль пользователя
from app import alltrail  # Просмотр всех маршрутов
from app import update_profile  # Обновление данных профиля
from app import update_trail  # Обновление информации о маршрутах
from app import update_trip  # Обновление информации о поездках
from app import notification  # Уведомления для пользователей
from app import update_flight  # Обновление информации о рейсах
from app import create_route  # Создание маршрутов
from app import update_route  # Обновление данных маршрутов
from app import delete_route  # Удаление маршрутов
from app import users  # Управление пользователями
from app import role_required  # Ограничение доступа по ролям
from app import user_trail  # Маршруты, связанные с пользователями
from app import logout  # Выход из системы
from app import flash_handler