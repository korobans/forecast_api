import os
import shutil
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from forecasts.src.closest_station import calculate_closest_stations
from forecasts.src.extract_data_from_database import get_weather_data, generating_stations
from forecasts.src.area_separator import separator
from forecasts.src.values_interpolator import interpolate_weather
from forecasts.src.geoTIFF_creator import create_geotiff
from forecasts.src.geoJSON_creator import create_geojson

app = FastAPI()

link = "../forecasts.db"


def extract_metric(metric, inter_data, n, m):
    temps_ = []
    [temps_.append(i[1][metric]) for i in inter_data]

    temps = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(temps_[i * m + j])
        temps.append(row)

    return np.array(temps)[::-1]


class WeatherRequest(BaseModel):
    lat1: float
    lon1: float
    lat2: float
    lon2: float
    n_width: int
    n_height: int
    date1: str
    hour1: str
    date2: str
    hour2: str


@app.get("/weather/")
async def get_weather(lat1: float, lon1: float, lat2: float, lon2: float, n_width: int, n_height: int, date1: str, hour1: str, date2: str, hour2: str):
    try:
        if os.path.exists("maps"):
            shutil.rmtree("maps")
            os.makedirs("maps")

        if os.path.exists("maps.zip"):
            os.remove("maps.zip")

        # Преобразуем указанные даты и часы в объекты datetime
        start_datetime = datetime.strptime(f"{date1} {hour1}", "%Y-%m-%d %H")
        end_datetime = datetime.strptime(f"{date2} {hour2}", "%Y-%m-%d %H")
        print(start_datetime, end_datetime)

        # Генерируем список дат и часов от start_datetime до end_datetime
        datetime_list = []
        current_datetime = start_datetime
        while current_datetime <= end_datetime:
            datetime_list.append(current_datetime)
            current_datetime += timedelta(hours=1)

        all_data = {}

        for dt in datetime_list:
            date_str = dt.strftime("%Y-%m-%d")
            hour_str = dt.strftime("%H")
            stations_data = get_weather_data(link, date_str, hour_str)
            weather_dict = {station: {'temp': temp, 'dwpt': dwpt, 'rhum': rhum, 'pres': pres} for station, temp, dwpt, rhum, pres in stations_data}

            [square_corners, square_centers] = separator(lat1, lon1, lat2, lon2, n_width, n_height)

            df = generating_stations(link)

            interpolated_data = []
            for center in square_centers:
                closest_stations = calculate_closest_stations(df, center[0], center[1], 20)
                interpolated_values = interpolate_weather(closest_stations, weather_dict)
                if interpolated_values is not None:
                    interpolated_data.append([center, interpolated_values])

            timestamp = dt.strftime('%Y_%m_%d_%H')

            temps = extract_metric('temp', interpolated_data, n_height, n_width)
            dwpts = extract_metric('dwpt', interpolated_data, n_height, n_width)
            rhums = extract_metric('rhum', interpolated_data, n_height, n_width)
            presses = extract_metric('pres', interpolated_data, n_height, n_width)

            geotiff_temp_filename = create_geotiff(temps, lat1, lon1, lat2, lon2, timestamp, 'temp')
            geotiff_rhum_filename = create_geotiff(rhums, lat1, lon1, lat2, lon2, timestamp, 'rhum')
            geotiff_pres_filename = create_geotiff(presses, lat1, lon1, lat2, lon2, timestamp, 'pres')
            geotiff_dwpt_filename = create_geotiff(dwpts, lat1, lon1, lat2, lon2, timestamp, 'dwpt')
            geojson_temp_filename = create_geojson(interpolated_data, square_corners, 'temp', timestamp)
            geojson_dwpt_filename = create_geojson(interpolated_data, square_corners, 'dwpt', timestamp)
            geojson_rhum_filename = create_geojson(interpolated_data, square_corners, 'rhum', timestamp)
            geojson_pres_filename = create_geojson(interpolated_data, square_corners, 'pres', timestamp)

        # Создаем zip файл с папкой maps
        zip_file_path = "maps.zip"
        shutil.make_archive("maps", 'zip', "maps")

        response = FileResponse(zip_file_path, filename="maps.zip")

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
