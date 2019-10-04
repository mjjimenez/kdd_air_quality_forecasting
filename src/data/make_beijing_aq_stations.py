# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np

def process_aq_stations(df):
    df = df.loc[11:].dropna().reset_index().drop('index', axis=1)
    return df

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 

    beijing_aq_stations = pd.read_excel(f'{input_filepath}/Beijing_AirQuality_Stations_en.xlsx', names=['station_id', 'longitude', 'latitude'])
    beijing_aq_stations = process_aq_stations(beijing_aq_stations)
    beijing_aq_stations.to_feather(f'{output_filepath}/beijing_aq_stations.feather')

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
