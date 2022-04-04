import os
import pandas as pd

import config
from zipfile import ZipFile


if __name__ == '__main__':

    # read dataframes
    df_f = pd.read_csv('dataset/fotocasa.csv')
    df_i = pd.read_csv('dataset/idealista.csv')

    df_f['source'] = config.FOTOCASA_ID
    df_i['source'] = config.IDEALISTA_ID

    # concat dataframes
    df_merged = pd.concat([df_f,df_i])

    df_merged.to_csv('dataset/merged.csv')

