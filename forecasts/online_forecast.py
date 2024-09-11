import asyncio
import shutil
import os
import uuid
import zipfile
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from forecasts.src.closest_station import calculate_closest_stations
from forecasts.src.extract_data_from_database import get_weather_data, generating_stations
from forecasts.src.area_separator import separator_for_json
from forecasts.src.values_interpolator import interpolate_weather
from forecasts.src.geoTIFF_creator import create_geotiff_async
from forecasts.src.geoJSON_creator import create_geojson
import atexit

app = FastAPI()


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


def clear_maps_folder():
    folder = 'maps'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def delete_zip_files():
    for filename in os.listdir('.'):
        if filename.endswith('.zip'):
            os.remove(filename)


class WeatherRequest(BaseModel):
    lat1: float
    lon1: float
    lat2: float
    lon2: float
    n_width: int
    n_height: int
    date: str
    hour: str
    temp_m: int
    dwpt_m: int
    rhum_m: int
    pres_m: int
    wdir_m: int
    wspd_m: int


@app.get("/weather_geojson/")
async def get_geojson(lat1: float, lon1: float, lat2: float, lon2: float, n_width: int, n_height: int, date: str, hour: str, temp_m: int, dwpt_m: int, rhum_m: int, pres_m: int, wdir_m: int, wspd_m: int):
    response = []
    try:
        needed_metrics = []
        if temp_m:
            needed_metrics.append('temp')
        if dwpt_m:
            needed_metrics.append('dwpt')
        if rhum_m:
            needed_metrics.append('rhum')
        if pres_m:
            needed_metrics.append('pres')
        if wdir_m:
            needed_metrics.append('wdir')
        if wspd_m:
            needed_metrics.append('wspd')

        # Преобразуем указанные даты и часы в объекты datetime
        end_datetime = datetime.strptime(f"{date} {hour}", "%Y-%m-%d %H")
        start_datetime = datetime.strptime(f"{date} {int(hour) - 4}", "%Y-%m-%d %H")  # Текущая дата и время

        # Генерируем список дат и часов от start_datetime до end_datetime
        datetime_list = []
        current_datetime = start_datetime
        print(current_datetime)
        print(end_datetime)
        while current_datetime <= end_datetime:
            datetime_list.append(current_datetime)
            current_datetime += timedelta(hours=1)

        for dt in datetime_list:
            date_str = dt.strftime("%Y-%m-%d")
            hour_str = dt.strftime("%H")
            stations_data = get_weather_data(date_str, hour_str)
            weather_dict = {station: {'temp': temp, 'dwpt': dwpt, 'rhum': rhum, 'wdir': wdir, 'wspd': wspd, 'pres': pres} for station, temp, dwpt, rhum, wdir, wspd, pres in stations_data}
            square_centers = separator_for_json(lat1, lon1, lat2, lon2, n_width, n_height)

            df = generating_stations()

            interpolated_data = []
            for center in square_centers:
                closest_stations = calculate_closest_stations(df, center[0], center[1], 7)
                interpolated_values = interpolate_weather(closest_stations, weather_dict)
                if interpolated_values is not None:
                    interpolated_data.append([center, interpolated_values])

            response.append(create_geojson(interpolated_data, needed_metrics))
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather_geotiff/")
async def get_geotiff(lat1: float, lon1: float, lat2: float, lon2: float, n_width: int, n_height: int, date: str, hour: str, temp_m: int, dwpt_m: int, rhum_m: int, pres_m: int, wdir_m: int, wspd_m: int):
    try:
        needed_metrics = []
        if temp_m:
            needed_metrics.append('temp')
        if dwpt_m:
            needed_metrics.append('dwpt')
        if rhum_m:
            needed_metrics.append('rhum')
        if pres_m:
            needed_metrics.append('pres')
        if wdir_m:
            needed_metrics.append('wdir')
        if wspd_m:
            needed_metrics.append('wspd')

        end_datetime = datetime.strptime(f"{date} {hour}", "%Y-%m-%d %H")
        start_datetime = datetime.strptime(f"{date} {int(hour) - 4}", "%Y-%m-%d %H")  # Текущая дата и время

        datetime_list = []
        current_datetime = start_datetime
        while current_datetime <= end_datetime:
            datetime_list.append(current_datetime)
            current_datetime += timedelta(hours=1)

        unique_folder = str(uuid.uuid4())
        os.makedirs(unique_folder, exist_ok=True)

        tasks = []
        for dt in datetime_list:
            date_str = dt.strftime("%Y-%m-%d")
            hour_str = dt.strftime("%H")
            stations_data = get_weather_data(date_str, hour_str)
            weather_dict = {station: {'temp': temp, 'dwpt': dwpt, 'rhum': rhum, 'wdir': wdir, 'wspd': wspd, 'pres': pres} for station, temp, dwpt, rhum, wdir, wspd, pres in stations_data}
            square_centers = separator_for_json(lat1, lon1, lat2, lon2, n_width, n_height)

            df = generating_stations()

            interpolated_data = []
            for center in square_centers:
                closest_stations = calculate_closest_stations(df, center[0], center[1], 7)
                interpolated_values = interpolate_weather(closest_stations, weather_dict)
                if interpolated_values is not None:
                    interpolated_data.append([center, interpolated_values])

            timestamp = dt.strftime('%Y_%m_%d_%H')

            if 'temp' in needed_metrics:
                temps = extract_metric('temp', interpolated_data, n_width, n_height)
                tasks.append(create_geotiff_async(temps, lat1, lon1, lat2, lon2, timestamp, 'temp', unique_folder))
            if 'dwpt' in needed_metrics:
                dwpts = extract_metric('dwpt', interpolated_data, n_width, n_height)
                tasks.append(create_geotiff_async(dwpts, lat1, lon1, lat2, lon2, timestamp, 'dwpt', unique_folder))
            if 'rhum' in needed_metrics:
                rhums = extract_metric('rhum', interpolated_data, n_width, n_height)
                tasks.append(create_geotiff_async(rhums, lat1, lon1, lat2, lon2, timestamp, 'rhum', unique_folder))
            if 'pres' in needed_metrics:
                presses = extract_metric('pres', interpolated_data, n_width, n_height)
                tasks.append(create_geotiff_async(presses, lat1, lon1, lat2, lon2, timestamp, 'pres', unique_folder))
            if 'wdir' in needed_metrics:
                wdirs = extract_metric('wdir', interpolated_data, n_width, n_height)
                tasks.append(create_geotiff_async(wdirs, lat1, lon1, lat2, lon2, timestamp, 'wdir', unique_folder))
            if 'wspd' in needed_metrics:
                wspds = extract_metric('wspd', interpolated_data, n_width, n_height)
                tasks.append(create_geotiff_async(wspds, lat1, lon1, lat2, lon2, timestamp, 'wspd', unique_folder))

        await asyncio.gather(*tasks)

        zip_filename = f'{unique_folder}.zip'
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, dirs, files in os.walk(unique_folder):
                for file in files:
                    if file.endswith('.tif'):
                        zipf.write(os.path.join(root, file), file)

        return FileResponse(zip_filename, media_type='application/zip', filename=zip_filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/info')
def get_param_info(): return {'lat1': 'Широта 1-ой точки в десятичном формате, Вещественное число',
                              'lon1': 'Долгота 1-ой точки в десятичном формате, Вещественное число',
                              'lat2': 'Широта 2-ой точки в десятичном формате, Вещественное число',
                              'lon2': 'Долгота 2-ой точки в десятичном формате, Вещественное число',
                              'n_width': 'Количество прямоугольников по широте, Целое число',
                              'n_height': 'Количество прямоугольников по высоте, Целое число',
                              'date': 'Дата окончания прогноза, YYYY-MM-DD',
                              'hour': 'Час окончания прогноза, HH',
                              'temp_m': 'Параметр, добавляющий в ответ информацию о температуре, 1/0',
                              'dwpt_m': 'Параметр, добавляющий в ответ информацию о точке росы, 1/0',
                              'rhum_m': 'Параметр, добавляющий в ответ информацию о влажности, 1/0',
                              'pres_m': 'Параметр, добавляющий в ответ информацию о давлении, 1/0',
                              'wdir_m': 'Параметр, добавляющий в ответ информацию о направлении ветра, 1/0',
                              'wspd_m': 'Параметр, добавляющий в ответ информацию о скорости ветра, 1/0'}


@app.on_event("shutdown")
def on_shutdown():
    delete_zip_files()
    clear_maps_folder()


if __name__ == "__main__":
    import uvicorn
    atexit.register(delete_zip_files)  # Удаление zip файлов при остановке сервера
    uvicorn.run(app, host="127.0.0.1", port=8000)