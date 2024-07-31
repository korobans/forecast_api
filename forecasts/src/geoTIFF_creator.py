import numpy as np
import folium
import rasterio
from rasterio.transform import from_bounds
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def create_geotiff(data, lat1, lon1, lat2, lon2, timestamp, datatype):
    n, m = data.shape

    # Задаем размеры изображения и разрешение (ширина и высота в пикселях)
    width, height = 600, 600

    # Задаем координаты углов (географические координаты границ области)
    min_lon, min_lat = min(lon1, lon2), min(lat1, lat2)  # Примерные координаты юго-западного угла
    max_lon, max_lat = max(lon1, lon2), max(lat1, lat2)  # Примерные координаты северо-восточного угла

    min_lon *= 0.995
    min_lat *= 0.995
    max_lon *= 1.005
    max_lat *= 1.005

    # Создаем пустое изображение
    image = np.zeros((height, width, 3), dtype=np.uint8)

    if datatype == 'temp':
        # Создание цветовой карты от белого до красного
        cmap = LinearSegmentedColormap.from_list('white_to_red', ['white', 'red'])

    elif datatype == 'dwpt':
        cmap = LinearSegmentedColormap.from_list('green_to_red', ['green', 'red'])

    elif datatype == 'rhum':
        cmap = LinearSegmentedColormap.from_list('yellow_to_purple', ['yellow', 'purple'])

    else:
        spectral_colors = ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00', '#FF7F00', '#FF0000']
        cmap = LinearSegmentedColormap.from_list('spectral', spectral_colors)

    # Нормализация данных
    normalized_data = (data - data.min()) / (data.max() - data.min())

    # Координаты для сетки
    x_coords = np.linspace(0, width, m + 1).astype(int)
    y_coords = np.linspace(0, height, n + 1).astype(int)

    # Наложение данных на изображение с использованием цветовой карты
    for i in range(n):
        for j in range(m):
            color = cmap(normalized_data[i, j])[:3]
            color = (np.array(color) * 255).astype(np.uint8)
            image[y_coords[i]:y_coords[i+1], x_coords[j]:x_coords[j+1]] = color

    # Определение трансформации для геопривязки
    transform = from_bounds(min_lon, min_lat, max_lon, max_lat, width, height)

    # Метаданные для GeoTIFF
    meta = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': 3,  # RGB изображение
        'dtype': 'uint8',
        'crs': 'EPSG:4326',  # Координаты в формате WGS84
        'transform': transform
    }

    # Сохранение изображения в GeoTIFF
    output_tiff_path = f'maps/{datatype}_{timestamp}.tif'
    with rasterio.open(output_tiff_path, 'w', **meta) as dst:
        for k in range(3):
            dst.write(image[:, :, k], k + 1)
        # Запись исходных данных в метаданные
        dst.update_tags(data=str(data.tolist()))

    return output_tiff_path
