import sqlite3
import pandas as pd


def generating_stations(link):
    conn = sqlite3.connect(link)

    # Запрос для извлечения данных из таблицы stations
    query = "SELECT id, latitude, longitude FROM stations WHERE id IN (SELECT DISTINCT station FROM data)"

    # Чтение данных в датафрейм
    df = pd.read_sql_query(query, conn)

    # Закрытие соединения с базой данных
    conn.close()

    return df


def get_weather_data(db_path: str, date: str, hour: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"""
    SELECT station, temp, dwpt, rhum, pres
    FROM data
    WHERE date LIKE '{date}%' AND hour = '{hour}'
    """
    cursor.execute(query)

    data = cursor.fetchall()
    conn.close()

    return data