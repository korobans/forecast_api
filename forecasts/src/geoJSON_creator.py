import folium
import json
from branca.colormap import linear


def create_geojson(square_data, square_corners, metric, timestamp):
    features = []
    metric_values = [data[1][metric] for data in square_data]
    min_metric = min(metric_values)
    max_metric = max(metric_values)

    if metric == 'temp':
        colormap = linear.YlOrRd_09.scale(min_metric, max_metric)
    elif metric == 'rhum':
        colormap = linear.YlGn_09.scale(min_metric, max_metric)
    elif metric == 'dwpt':
        colormap = linear.PuBuGn_09.scale(min_metric, max_metric)
    elif metric == 'pres':
        colormap = linear.Spectral_09.scale(min_metric, max_metric)
    else:
        raise ValueError("Unsupported metric")

    for i, part in enumerate(square_corners):
        rec_bounds = [part[0], part[1], part[2], part[3]]
        metric_value = square_data[i][1][metric]
        color = colormap(metric_value)

        # Преобразование цвета в строку, если это ndarray
        if hasattr(color, 'tolist'):
            color = color.tolist()
        color = str(color)

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [rec_bounds[0][1], rec_bounds[0][0]],
                    [rec_bounds[1][1], rec_bounds[1][0]],
                    [rec_bounds[2][1], rec_bounds[2][0]],
                    [rec_bounds[3][1], rec_bounds[3][0]],
                    [rec_bounds[0][1], rec_bounds[0][0]]
                ]]
            },
            "properties": {
                metric: metric_value,
                "color": color
            }
        }
        features.append(feature)

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    filename = f"maps/{metric}_{timestamp}.geojson"
    with open(filename, 'w') as f:
        json.dump(geojson_data, f, indent=2)

    return filename
