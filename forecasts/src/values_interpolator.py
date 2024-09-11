import numpy as np


def interpolate_weather(stations, weather_dict):
    valid_stations = [(station, dist) for station, dist in stations if station in weather_dict]
    if not valid_stations:
        return None

    distances = np.array([dist for _, dist in valid_stations])
    inverse_distances = 1 / distances
    weights = inverse_distances / np.sum(inverse_distances)
    parameters = ['temp', 'dwpt', 'rhum', 'wdir', 'wspd', 'pres']

    weighted_values = {}
    for parameter in parameters:
        values = np.array([weather_dict[station][parameter] for station, _ in valid_stations])
        weighted_values[parameter] = np.sum(values * weights)

    return weighted_values