import os
import re
from zipfile import ZipFile

import pandas as pd

from . import config, utils


def merge_idealista_files():
    """
    Merges files from idealista individual location scraping
    """
    regex = re.compile('.*idealista-.*[.]csv$')
    csvs = utils.get_files_in_directory(config.DATASET_DIR, extension='.csv')
    dfs = [pd.read_csv(csv_file) for csv_file in csvs if regex.match(csv_file)]
    if len(dfs) > 0:
        idealista_csv = pd.concat(dfs).drop_duplicates('id')
        idealista_csv.to_csv(config.IDEALISTA_FILE, encoding='utf-8',
                             index=False, header=True)


def merge_idealista_folders():
    """
    Merges folders from idealista individual location scraping
    """
    regex = re.compile('.*idealista-.*$')
    folders = [folder for folder in utils.get_directories(
        config.DATASET_DIR) if regex.match(folder)]
    if not utils.directory_exists(config.IDEALISTA_MAPS):
        [utils.duplicate_folder(dir=folder, dest=config.IDEALISTA_MAPS) for folder in folders]

def merge_fotocasa_files():
    """
    Merges files from fotocasa individual location scraping
    """
    regex = re.compile('.*fotocasa.*[.]csv$')
    csvs = utils.get_files_in_directory(config.DATASET_DIR, extension='.csv')
    dfs = [pd.read_csv(csv_file) for csv_file in csvs if regex.match(csv_file)]
    if len(dfs) > 0:
        fotocasa_csv = pd.concat(dfs).drop_duplicates('id')
        fotocasa_csv.to_csv(config.FOTOCASA_FILE, encoding='utf-8',
                             index=False, header=True)

def merge_fotocasa_folders():
    """
    Merges folders from fotocasa individual location scraping
    """
    regex = re.compile('.*fotocasa-.*$')
    folders = [folder for folder in utils.get_directories(
        config.DATASET_DIR) if regex.match(folder)]
    if not utils.directory_exists(config.FOTOCASA_IMG_DIR):
        [utils.duplicate_folder(dir=folder, dest=config.FOTOCASA_IMG_DIR) for folder in folders]

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
    df_merged = pd.concat([df_f, df_i])
    df_merged.to_csv(config.MERGED_FILE)


def zip_everything():
    """
    Compresses resulting files
    """
    zip_file = ZipFile(config.MERGED_ZIP_FILE, 'w')
    zip_file.write(filename=config.MERGED_FILE, arcname=os.path.basename(config.MERGED_FILE))
    zip_file.write(filename=config.IDEALISTA_MAPS, arcname=os.path.basename(config.IDEALISTA_MAPS))
    zip_file.write(filename=config.FOTOCASA_IMG_DIR, arcname=os.path.basename(config.FOTOCASA_IMG_DIR))

    for folder_name, _, files in os.walk(config.IDEALISTA_MAPS):
        for file in files:
            file_name = os.path.join(folder_name, file)
            arc_name = os.path.relpath(file_name, os.path.join(config.IDEALISTA_MAPS, '..'))
            zip_file.write(filename=file_name, arcname=arc_name)
            
    for folder_name, _, files in os.walk(config.FOTOCASA_IMG_DIR):
        for file in files:
            file_name = os.path.join(folder_name, file)
            arc_name = os.path.relpath(file_name, os.path.join(config.FOTOCASA_IMG_DIR, '..'))
            zip_file.write(filename=file_name, arcname=arc_name)

    zip_file.close()


if __name__ == '__main__':
    merge_idealista_files()
    merge_idealista_folders()

    merge_fotocasa_files()
    merge_fotocasa_folders()

    merge_fotocasa_idealista()
    zip_everything()
