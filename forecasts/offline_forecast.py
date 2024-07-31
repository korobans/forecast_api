from forecasts.src.closest_station import calculate_closest_stations
from forecasts.src.extract_data_from_database import get_weather_data, generating_stations
from forecasts.src.area_separator import separator
from forecasts.src.values_interpolator import interpolate_weather
from forecasts.src.geoTIFF_creator import map_constructor_rhum, map_constructor_temp, map_constructor_pres


link = "../archive.db"
lat1, lon1 = map(float, input('Начало:').split())
lat2, lon2 = map(float, input('Конец:').split())
n_width, n_height = map(int, input('Разрешение (Широта * Долгота)').split())
date, hour = input('Дата и время(MM-DD HH)').split()
date = f"2000-{date}"

stations_data = get_weather_data(link, date, hour)
weather_dict = {station: {'temp': temp, 'dwpt': dwpt, 'rhum': rhum, 'pres': pres} for station, temp, dwpt, rhum, pres in stations_data}

[square_corners, square_centers] = separator(lat1, lon1, lat2, lon2, n_width, n_height)

df = generating_stations(link)

interpolated_data = []
for center in square_centers:
    closest_stations = calculate_closest_stations(df, center[0], center[1], 10)
    interpolated_values = interpolate_weather(closest_stations, weather_dict)
    if interpolated_values is not None:
        interpolated_data.append([center, interpolated_values])

map_constructor_temp(interpolated_data, square_corners)
map_constructor_rhum(interpolated_data, square_corners)
map_constructor_pres(interpolated_data, square_corners)
