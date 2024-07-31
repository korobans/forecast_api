import pandas as pd
import sqlite3


def correct_table_creator(link):
    conn = sqlite3.connect(link)

    query = "SELECT * FROM data"
    data = pd.read_sql_query(query, conn)

    # Создание временного столбца 'timestamp'
    data['timestamp'] = pd.to_datetime(data['date'] + ' ' + data['hour'].astype(str) + ':00:00')

    # Установка 'timestamp' в качестве индекса
    data.set_index('timestamp', inplace=True)

    # Удаление столбцов 'date' и 'hour', так как они больше не нужны
    data.drop(columns=['date', 'hour'], inplace=True)

    # Интерполяция данных на каждый час
    hourly_data = data.groupby('station').apply(lambda group: group.resample('h').interpolate(method='linear'))

    # Сброс мультииндекса, созданного resample
    hourly_data.reset_index(level=0, drop=True, inplace=True)

    # Восстановление столбцов 'date' и 'hour'
    hourly_data['date'] = hourly_data.index.date
    hourly_data['hour'] = hourly_data.index.hour

    # Переупорядочивание столбцов
    hourly_data = hourly_data[
        ['date', 'hour', 'temp', 'dwpt', 'rhum', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun', 'coco', 'station']
    ]

    hourly_data.reset_index(drop=True, inplace=True)

    # Заполнение пропусков в столбце 'station'
    hourly_data['station'] = hourly_data['station'].ffill()

    # Округление значений
    columns_to_round = ['temp', 'dwpt', 'rhum', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']
    hourly_data[columns_to_round] = hourly_data[columns_to_round].round(1)

    # Сохранение интерполированных данных обратно в базу данных
    hourly_data.to_sql('data', conn, if_exists='replace', index=False)

    conn.close()

