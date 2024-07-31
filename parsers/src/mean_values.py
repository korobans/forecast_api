import sqlite3
import pandas as pd


def process_database(link):
    # Подключение к базе данных
    conn = sqlite3.connect(link)
    cursor = conn.cursor()

    # Загрузка данных из таблицы в DataFrame
    query = "SELECT * FROM data"
    df = pd.read_sql_query(query, conn)
    print(df.size)

    # Преобразование столбца 'date' в datetime
    df['date'] = pd.to_datetime(df['date'])

    # Группировка данных по году, месяцу, дате, часу и станции
    grouped = df.groupby([df['date'].dt.year, df['date'].dt.month, df['date'].dt.day, 'hour', 'station']).agg({
        'temp': 'mean',
        'dwpt': 'mean',
        'rhum': 'mean',
        'prcp': lambda x: x.mode()[0] if not x.mode().empty else None,
        'snow': lambda x: x.mode()[0] if not x.mode().empty else None,
        'wdir': 'mean',
        'wspd': 'mean',
        'wpgt': 'mean',
        'pres': 'mean',
        'tsun': lambda x: x.mode()[0] if not x.mode().empty else None,
        'coco': lambda x: x.mode()[0] if not x.mode().empty else None
    }).reset_index()

    # Преобразование года, месяца и дня обратно в формат даты
    grouped['date'] = pd.to_datetime(grouped[['date', 'date_1', 'date_2']].rename(columns={'date': 'year', 'date_1': 'month', 'date_2': 'day'}))
    grouped = grouped.drop(columns=['date_1', 'date_2'])

    # Замена '-' на None в текстовых полях
    text_fields = ['prcp', 'snow', 'tsun', 'coco']
    for field in text_fields:
        grouped[field] = grouped[field].replace('-', None)

    # Удаление исходной таблицы
    cursor.execute("DROP TABLE data")

    # Создание новой таблицы с тем же именем
    cursor.execute('''
    CREATE TABLE "data" (
        "date"	DATE,
        "hour"	INTEGER,
        "temp"	REAL,
        "dwpt"	REAL,
        "rhum"	REAL,
        "prcp"	TEXT,
        "snow"	TEXT,
        "wdir"	REAL,
        "wspd"	REAL,
        "wpgt"	REAL,
        "pres"	REAL,
        "tsun"	TEXT,
        "coco"	TEXT,
        "station"	TEXT
    );
    ''')

    # Вставка обработанных данных обратно в базу данных
    grouped.to_sql('data', conn, if_exists='replace', index=False)

    # Закрытие соединения с базой данных
    conn.close()
