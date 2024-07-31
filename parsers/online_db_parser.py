import shutil
import os
from parsers.src.data_extractor import extract_stations
from parsers.src.downloader import download_stations
from parsers.src.unarchivator import unarchive
from parsers.src.headers import set_headers
from parsers.src.script import add_tables
from parsers.src.empty_values_filler import correct_table_creator


if __name__ == "__main__":
    link = '../forecasts.db'
    #try:
    #    shutil.rmtree('archives')
    #    shutil.rmtree('extracted')
    #    os.remove(link)
    #except Exception: pass
    #os.mkdir('archives')
    #os.mkdir('extracted')
    #download_stations(False)
    #extract_stations(link)
    unarchive()
    set_headers()
    add_tables(link, False)
    correct_table_creator(link)
    try:
        shutil.rmtree('archives')
        shutil.rmtree('extracted')
    except Exception: pass
