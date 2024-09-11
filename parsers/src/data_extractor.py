import sqlite3
import pandas as pd
import webbrowser
import time


def extract_stations(link):
    conn = sqlite3.connect(link)
    query = "SELECT id FROM stations WHERE country = 'RU'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    for i in range(df.size):
        print(f"https://bulk.meteostat.net/v2/hourly/{df.loc[i].id}.csv.gz")
        webbrowser.open(f"https://bulk.meteostat.net/v2/hourly/{df.loc[i].id}.csv.gz", new=0, autoraise=True)
        time.sleep(0.5)
