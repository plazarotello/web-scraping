import re
from zipfile import ZipFile

import pandas as pd

from . import config, utils


def merge_idealista_files():
    """
    Merges files from idealista individual location scraping
    """
    regex = re.compile('idealista-*[.]csv$')
    csvs = utils.get_files_in_directory(config.DATASET_DIR, extension='.csv')
    dfs = [pd.read_csv(csv_file) for csv_file in csvs if regex.match(csv_file)]
    idealista_csv = pd.concat(dfs).drop_duplicates('id')
    idealista_csv.to_csv(config.IDEALISTA_FILE, encoding='utf-8',
                         index=False, header=True)


def merge_idealista_folders():
    """
    Merges folders from idealista individual location scraping
    """
    regex = re.compile('^idealista-*$')
    folders = [folder for folder in utils.get_directories(
        config.DATASET_DIR) if regex.match(folder)]
    utils.create_directory(config.IDEALISTA_MAPS)
    map(utils.duplicate_folder(dest=config.IDEALISTA_MAPS), folders)


def merge_fotocasa_idealista():
    """
    Merges files from Fotocasa and Idealista .csv and creates a new column to identify its source
    """
    # read dataframes
    df_f = pd.read_csv(config.FOTOCASA_FILE)
    df_i = pd.read_csv(config.IDEALISTA_FILE)
    df_f['source'] = config.FOTOCASA_ID
    df_i['source'] = config.IDEALISTA_ID

    # concat dataframes
    df_merged = pd.concat([df_f,df_i])
    df_merged.to_csv(config.MERGED_FILE)


def zip_everything():
    """
    Compresses resulting files
    """
    zip_file = ZipFile(config.MERGED_ZIP_FILE, 'w')
    zip_file.write(config.MERGED_FILE)
    zip_file.write(config.IDEALISTA_MAPS)
    zip_file.write(config.FOTOCASA_IMG_DIR)
    zip_file.close()


if __name__ == '__main__':
    merge_idealista_files()
    merge_idealista_folders()
    merge_fotocasa_idealista()
    zip_everything()
