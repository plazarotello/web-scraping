import os
import pandas as pd

from scraper.misc import config
from zipfile import ZipFile


if __name__ == '__main__':

    # read dataframes
    df_f = pd.read_csv(config.FOTOCASA_FILE)
    df_i = pd.read_csv(config.IDEALISTA_FILE)

    # concat dataframes
    df_merged = pd.concat(df_f,df_i)

    df_merged.to_csv(config.MERGED_FILE)

    #crearte zip file with content
    zipObj = ZipFile(config.MERGED__ZIP_FILE, 'w')
    zipObj.write(config.MERGED_FILE)
    zipObj.close()

    # remove old csv dataframe
    os.remove(config.MERGED_FILE)
