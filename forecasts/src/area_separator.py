def separator(lat1, lon1, lat2, lon2, n_width, n_height):
    width_deg = abs(lon2 - lon1)
    height_deg = abs(lat2 - lat1)

    coef = ((width_deg + height_deg) / 2) * 0.2

    width_deg += coef
    height_deg += coef

    center_lat = (lat1 + lat2) / 2
    center_lon = (lon1 + lon2) / 2
    lat1 = center_lat - height_deg / 2
    lat2 = center_lat + height_deg / 2
    lon1 = center_lon - width_deg / 2
    lon2 = center_lon + width_deg / 2

    part_width = width_deg / n_width
    part_height = height_deg / n_height

    corners = []
    centers = []

    for i in range(n_height):
        for j in range(n_width):
            corner1 = [lat1 + i * part_height, lon1 + j * part_width]
            corner2 = [lat1 + i * part_height, lon1 + (j + 1) * part_width]
            corner3 = [lat1 + (i + 1) * part_height, lon1 + (j + 1) * part_width]
            corner4 = [lat1 + (i + 1) * part_height, lon1 + j * part_width]

            center = [lat1 + (i + 0.5) * part_height, lon1 + (j + 0.5) * part_width]

            corners.append([corner1, corner2, corner3, corner4])
            centers.append(center)

    return [corners, centers]

