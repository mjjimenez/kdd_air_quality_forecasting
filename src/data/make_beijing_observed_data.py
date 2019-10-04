# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
import sys

def rename_weather_data(df):
    return df.rename(columns={'stationName': 'station_id', 'utc_time': 'utc_datetime', 'wind_speed/kph': 'wind_speed'})

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 

    beijing_meo_observed_17_18 = pd.read_csv(f'{input_filepath}/beijing_17_18_meo.csv', parse_dates=['utc_time'])
    beijing_meo_observed_802_803 = pd.read_csv(f'{input_filepath}/beijing_201802_201803_me.csv', parse_dates=['utc_time'])

    beijing_meo_observed_17_18 = rename_weather_data(beijing_meo_observed_17_18)
    beijing_meo_observed_802_803 = rename_weather_data(beijing_meo_observed_802_803)

    beijing_observed_meo_union = pd.concat([beijing_meo_observed_17_18, beijing_meo_observed_802_803], sort=False)
    beijing_observed_meo_union = beijing_observed_meo_union.drop_duplicates()

    beijing_observed_meo_union.reset_index().drop('index', axis=1).to_feather(f'{output_filepath}/beijing_meo_observed_union.feather')

    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')
    logger.info(sys.path)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
