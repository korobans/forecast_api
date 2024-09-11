def create_geojson(square_data, metrics):
    features = []

    for i, part in enumerate(square_data):
        properties = {}
        for metric in metrics:
            metric_value = square_data[i][1].get(metric)  # Используем get для безопасного доступа к значению
            if metric_value is not None:
                properties[metric] = metric_value

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [part[0][0], part[0][1]]
            },
            "properties": properties
        }
        features.append(feature)

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    return geojson_data