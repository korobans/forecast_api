import sqlite3
import psycopg2


def trans(link):
    # Параметры подключения к базам данных
    sqlite_db_path = link
    postgres_db_config = {
        'dbname': 'weather',
        'user': 'postgres',
        'password': 'taro123123',
        'host': 'localhost',
        'port': '5432'
    }

    # Подключение к SQLite и получение данных
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()

    # Получение данных из таблицы data
    sqlite_cursor.execute("SELECT * FROM data")
    data_rows = sqlite_cursor.fetchall()

    # Получение данных из таблицы stations
    sqlite_cursor.execute("SELECT * FROM stations")
    stations_rows = sqlite_cursor.fetchall()

    # Подключение к PostgreSQL
    postgres_conn = psycopg2.connect(**postgres_db_config)
    postgres_cursor = postgres_conn.cursor()

    # Удаление таблиц data и stations, если они существуют
    drop_data_table_query = "DROP TABLE IF EXISTS data"
    drop_stations_table_query = "DROP TABLE IF EXISTS stations"
    postgres_cursor.execute(drop_data_table_query)
    postgres_cursor.execute(drop_stations_table_query)

    # Создание таблицы data в PostgreSQL
    create_data_table_query = """
    CREATE TABLE data (
        date DATE,
        hour INTEGER,
        temp REAL,
        dwpt REAL,
        rhum REAL,
        prcp TEXT,
        snow TEXT,
        wdir REAL,
        wspd REAL,
        wpgt TEXT,
        pres REAL,
        tsun TEXT,
        coco TEXT,
        station TEXT
    );
    """
    postgres_cursor.execute(create_data_table_query)

    # Создание таблицы stations в PostgreSQL
    create_stations_table_query = """
    CREATE TABLE stations (
        id CHAR(5) PRIMARY KEY,
        country VARCHAR(2) DEFAULT NULL,
        region VARCHAR(5) DEFAULT NULL,
        latitude FLOAT8 DEFAULT NULL,
        longitude FLOAT8 DEFAULT NULL,
        elevation INT DEFAULT NULL,
        timezone VARCHAR(30) DEFAULT NULL
    );
    """
    postgres_cursor.execute(create_stations_table_query)
    postgres_conn.commit()

    # Вставка данных в таблицу data в PostgreSQL
    insert_data_query = """
    INSERT INTO data (date, hour, temp, dwpt, rhum, prcp, snow, wdir, wspd, wpgt, pres, tsun, coco, station)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    postgres_cursor.executemany(insert_data_query, data_rows)

    # Вставка данных в таблицу stations в PostgreSQL
    insert_stations_query = """
    INSERT INTO stations (id, country, region, latitude, longitude, elevation, timezone)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    postgres_cursor.executemany(insert_stations_query, stations_rows)
    postgres_conn.commit()

    # Закрытие соединений
    sqlite_conn.close()
    postgres_cursor.close()
    postgres_conn.close()

    print("Перенос данных завершен.")
