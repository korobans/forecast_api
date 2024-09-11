import numpy as np
import rasterio
from rasterio.transform import from_bounds
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import os


async def create_geotiff_async(data, lat1, lon1, lat2, lon2, timestamp, datatype, output_folder):
    n, m = data.shape
    width, height = 600, 600
    min_lon, min_lat = min(lon1, lon2), min(lat1, lat2)
    max_lon, max_lat = max(lon1, lon2), max(lat1, lat2)
    min_lon *= 0.995
    min_lat *= 0.995
    max_lon *= 1.005
    max_lat *= 1.005
    image = np.zeros((height, width, 3), dtype=np.uint8)

    if datatype == 'temp':
        cmap = LinearSegmentedColormap.from_list('white_to_red', ['white', 'red'])
    elif datatype == 'dwpt':
        cmap = LinearSegmentedColormap.from_list('green_to_red', ['green', 'red'])
    elif datatype == 'rhum':
        cmap = LinearSegmentedColormap.from_list('yellow_to_purple', ['yellow', 'purple'])
    elif datatype == 'wdir':
        cmap = LinearSegmentedColormap.from_list('blue_to_red_to_blue', ['red', 'yellow', 'blue', 'yellow', 'red'])
    else:
        spectral_colors = ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00', '#FF7F00', '#FF0000']
        cmap = LinearSegmentedColormap.from_list('spectral', spectral_colors)

    if datatype == 'wdir':
        normalized_data = data / 360.0
    else:
        normalized_data = (data - data.min()) / (data.max() - data.min())

    x_coords = np.linspace(0, width, m + 1).astype(int)
    y_coords = np.linspace(0, height, n + 1).astype(int)

    for i in range(n):
        for j in range(m):
            color = cmap(normalized_data[i, j])[:3]
            color = (np.array(color) * 255).astype(np.uint8)
            image[y_coords[i]:y_coords[i+1], x_coords[j]:x_coords[j+1]] = color

    transform = from_bounds(min_lon, min_lat, max_lon, max_lat, width, height)

    meta = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': 3,
        'dtype': 'uint8',
        'crs': 'EPSG:4326',
        'transform': transform
    }

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image, extent=(0, width, height, 0))

    if datatype == 'wdir':
        for i in range(n):
            for j in range(m):
                angle = data[i, j]
                x_center = float((x_coords[j] + x_coords[j + 1]) / 2)
                y_center = float((y_coords[i] + y_coords[i + 1]) / 2)
                dx = float(np.sin(np.radians(angle)) * 10)
                dy = float(-np.cos(np.radians(angle)) * 10)
                ax.arrow(x_center, y_center, dx, dy, head_width=5, head_length=5, fc='black', ec='black')

    plt.axis('off')
    png_path = os.path.join(output_folder, f'{datatype}_{timestamp}.png')
    plt.savefig(png_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

    image_with_arrows = plt.imread(png_path)

    output_tiff_path = os.path.join(output_folder, f'{datatype}_{timestamp}.tif')
    with rasterio.open(output_tiff_path, 'w', **meta) as dst:
        for k in range(3):
            dst.write((image_with_arrows[:, :, k] * 255).astype(np.uint8), k + 1)
        dst.update_tags(data=str(data.tolist()))

    # Удаление всех PNG файлов из папки
    for file_name in os.listdir(output_folder):
        if file_name.endswith('.png'):
            os.remove(os.path.join(output_folder, file_name))

    return output_tiff_path