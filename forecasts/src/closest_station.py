import math


def haversine(lat1, lon1, lat2, lon2):
    # Радиус Земли в километрах
    r = 6371.0

    # Перевод градусов в радианы
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Разница в координатах
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Формула Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Расстояние в километрах
    distance = r * c

    return distance


def calculate_closest_stations(df, latitude, longitude, n):
    nearest_stations = []

    for i, value in df.iterrows():
        dist = haversine(latitude, longitude, value['latitude'], value['longitude'])
        nearest_stations.append([value['id'], dist])

    return sorted(nearest_stations, key=lambda x: x[1])[:n]

