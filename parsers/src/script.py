import os
import sqlite3
import pandas as pd
from datetime import datetime


def add_tables(link, is_archive: bool):
    csv_folder_path = 'extracted'

    conn = sqlite3.connect(link)
    cursor = conn.cursor()

    for filename in os.listdir(csv_folder_path):
        if filename.endswith('.csv'):
            csv_file_path = os.path.join(csv_folder_path, filename)
            df = pd.read_csv(csv_file_path)
            df['date'] = pd.to_datetime(df['date'])

            if is_archive:
                # Calculate average values for each date and hour over the years
                df['month_day_hour'] = df['date'].dt.strftime('%m-%d') + ' ' + df['hour'].astype(str).str.zfill(2)

                # Filter out non-numeric columns except 'station' and 'coco'
                numeric_cols = df.select_dtypes(include=['number']).columns
                avg_df = df.groupby('month_day_hour').agg({**{col: 'mean' for col in numeric_cols}, 'station': 'first', 'coco': 'first'}).reset_index()

                # Round numeric columns to 2 decimal places, except the last column
                numeric_cols_to_round = numeric_cols[:-1]
                avg_df[numeric_cols_to_round] = avg_df[numeric_cols_to_round].round(2)

                def safe_date_parse(x):
                    try:
                        return datetime.strptime(x, '%m-%d %H').replace(year=2000)
                    except ValueError:
                        return None

                avg_df['date'] = avg_df['month_day_hour'].apply(safe_date_parse)
                avg_df = avg_df.drop(columns=['month_day_hour'])
                avg_df = avg_df.dropna(subset=['date'])  # Remove rows with invalid dates
            else:
                # Filter data for today and future dates
                today = datetime.today().strftime('%Y-%m-%d')
                df = df[df['date'] >= today]

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data (
                    date TEXT,
                    hour INTEGER,
                    temp REAL,
                    dwpt REAL,
                    rhum INTEGER,
                    prcp REAL,
                    snow INTEGER,
                    wdir INTEGER,
                    wspd REAL,
                    wpgt REAL,
                    pres REAL,
                    tsun INTEGER,
                    coco TEXT,
                    station TEXT
                )
            """)

            if is_archive:
                avg_df.to_sql('data', conn, if_exists='append', index=False)
            else:
                df.to_sql('data', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
