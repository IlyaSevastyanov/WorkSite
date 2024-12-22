from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp


class RegistrationForm(FlaskForm):
    # Имя
    first_name = StringField('Имя', [
        InputRequired(message='Имя обязательно для заполнения'),
        Length(min=1, max=100, message='Имя должно быть от 1 до 100 символов')
    ])

    # Фамилия
    surname = StringField('Фамилия', [
        InputRequired(message='Фамилия обязательна для заполнения'),
        Length(min=1, max=100, message='Фамилия должна быть от 1 до 100 символов')
    ])

    # E-mail (теперь логин)
    email = StringField('E-mail', [
        InputRequired(message='E-mail обязателен для заполнения'),
        Email(message='Введите корректный E-mail адрес')
    ])

    # Номер телефона
    phone_number = StringField('Номер телефона', [
        InputRequired(message='Номер телефона обязателен для заполнения'),
        Regexp(
            r'^\+?[\d\s\-\(\)]+$',
            message='Введите корректный номер телефона (например, +79991234567)'
        )
    ])

    # Пароль и его подтверждение
    password = PasswordField('Пароль', [
        InputRequired(message='Пароль обязателен для заполнения'),
        Length(min=6, max=100, message='Пароль должен содержать от 6 до 100 символов'),
        EqualTo('confirm', message='Пароли должны совпадать')
    ])
    confirm = PasswordField('Повторите пароль')

    # Кнопка отправки
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    # E-mail
    email = StringField('E-mail', [
        InputRequired(message='E-mail обязателен для заполнения'),
        Email(message='Введите корректный E-mail адрес')
    ])

    # Пароль
    password = PasswordField('Пароль', [
        InputRequired(message='Пароль обязателен для заполнения'),
        Length(min=6, max=100, message='Пароль должен содержать от 6 до 100 символов')
    ])

    # Кнопка отправки
    submit = SubmitField('Войти')
