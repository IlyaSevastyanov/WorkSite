import psycopg

try:
    with psycopg.connect(
        host="localhost",
        user="passenger",
        password="123",
        dbname="autobus"
    ) as con:
        print("Успешное подключение к базе данных!")
except Exception as e:
    print(f"Ошибка подключения: {e}")
