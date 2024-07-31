import webbrowser
import shutil


def download_stations(is_archive: bool):
    webbrowser.open("https://github.com/meteostat/weather-stations/raw/master/stations.db", new=0, autoraise=True)
    while True:
        try:
            if is_archive:
                shutil.move("archives/stations.db", "../archive.db")
            else:
                shutil.move("archives/stations.db", "../forecasts.db")
            break
        except Exception:
            pass
