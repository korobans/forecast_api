import os
import pandas as pd


def set_headers():
    folder_path = 'extracted'

    headers = ['date', 'hour', 'temp', 'dwpt', 'rhum', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun', 'coco', 'station']

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            
            df = pd.read_csv(file_path, header=None)
            
            df.columns = headers[:-1]  # Assign all headers except the last one
            df['station'] = os.path.splitext(filename)[0]  # Add the station name
            
            df.to_csv(file_path, index=False)

    print('Заголовки успешно добавлены ко всем CSV файлам в папке.')
