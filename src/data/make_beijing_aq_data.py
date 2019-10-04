# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np


def rename_aq_df(df):
    """ Renames any air quality station dataframe
    """
    return df.rename(columns={'stationId': 'station_id', 'utc_time': 'utc_datetime'})

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 

    # Merge all air quality data from two files. Rename their columns and save to an interim feather file
    beijing_17_18_aq = pd.read_csv(f'{input_filepath}/beijing_17_18_aq.csv', parse_dates=['utc_time'])
    beijing_802_803_aq = pd.read_csv(f'{input_filepath}/beijing_201802_201803_aq.csv', parse_dates=['utc_time'])
    beijing_17_18_aq = rename_aq_df(beijing_17_18_aq)
    beijing_802_803_aq = rename_aq_df(beijing_802_803_aq)

    beijing_aq_data = pd.concat([beijing_17_18_aq, beijing_802_803_aq], ignore_index=True)
    beijing_aq_data = beijing_aq_data.drop_duplicates()

    # `to_feather` won't accept the index after `drop_duplicates`. Had to `reset_index()` and drop the current index.
    beijing_aq_data.reset_index().drop('index', axis=1).to_feather(f'{output_filepath}/beijing_aq_union.feather')


    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
