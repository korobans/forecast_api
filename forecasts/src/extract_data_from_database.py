import pandas as pd
import psycopg2

# Параметры подключения к PostgreSQL
postgres_db_config = {
        'dbname': 'weather',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5432'
    }


def generating_stations():
    # Подключение к PostgreSQL
    conn = psycopg2.connect(**postgres_db_config)

    # Запрос для извлечения данных из таблицы stations
    query = "SELECT id, latitude, longitude FROM stations WHERE id IN (SELECT DISTINCT station FROM data)"

    # Чтение данных в датафрейм
    df = pd.read_sql_query(query, conn)

    # Закрытие соединения с базой данных
    conn.close()

    return df


def get_weather_data(date: str, hour: str):
    # Подключение к PostgreSQL
    conn = psycopg2.connect(**postgres_db_config)
    cursor = conn.cursor()

    query = f"""
    SELECT station, temp, dwpt, rhum, wdir, wspd, pres
    FROM data
    WHERE date::text LIKE '{date}%' AND hour = '{hour}'
    """
    cursor.execute(query)

    data = cursor.fetchall()
    conn.close()

    return data
