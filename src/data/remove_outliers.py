# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np

def process_air_quality_outliers(df):
    outliers_index = df[beijing_aq_data['PM2.5'] > 1400].index
    df = df.drop(outliers_index)
    return df

def process_observed_meo_outliers(df):
    df = df[df.temperature < 800000]
    df.loc[:, 'wind_direction'] = df.replace(999017, 0)
    return df

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 

    # Remove observed weather data outliers
    beijing_observed_meo_union = pd.read_feather(DATA_PATH + 'interim/beijing_meo_observed_union.feather')
    beijing_observed_meo_union = process_observed_meo_outliers(beijing_observed_meo_union)   

    beijing_observed_meo_union.reset_index().drop('index', axis=1).to_feather(DATA_PATH + 'interim/beijing_meo_observed_union.feather')

    # Remove air quality outliers
    beijing_aq_data = pd.read_feather(f'{input_filepath}/beijing_aq_union.feather') 
    beijing_aq_data = process_air_quality_outliers(beijing_aq_data)

    beijing_aq_data.reset_index().drop('index', axis=1).to_feather(DATA_PATH + 'interim/beijing_aq_union.feather')

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
