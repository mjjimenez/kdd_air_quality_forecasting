# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
import os

def split_vals(a,n): return a[:n].copy(), a[n:].copy()

def generate_train_test_data(df, target_column, split_ratio=None, split_date=None):

    if split_ratio is not None:
        split_index = int(len(df) * split_ratio)
    elif split_date is not None:
        date_index = df.index.get_loc(split_date)
        if type(date_index) == slice:
            split_index = date_index.start
        else:
            split_index = date_index
    else:
        raise("Must specify split ratio or split date")

    non_lagged_columns = list(df.columns[~df.columns.str.contains('\(.*\)')]) # lagged columns are labeled (t-1)
    non_lagged_columns.append(target_column)
    X = df.drop(non_lagged_columns, axis=1)
    y = df[target_column]


    X_train, X_valid = split_vals(X, split_index)
    y_train, y_valid = split_vals(y, split_index)


    return X_train, y_train, X_valid, y_valid


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 

    os.makedirs(f'{output_filepath}', exist_ok=True)
    
    donggaocun_pm25_supervised = pd.read_feather(f'{input_filepath}/donggaocun_aq_pm25_supervised_df.feather').set_index('utc_datetime')
    donggaocun_pm10_supervised = pd.read_feather(f'{input_filepath}/donggaocun_aq_pm10_supervised_df.feather').set_index('utc_datetime')
    donggaocun_O3_supervised = pd.read_feather(f'{input_filepath}/donggaocun_aq_O3_supervised_df.feather').set_index('utc_datetime')
    
    X_train_pm25, y_train_pm25, X_valid_pm25, y_valid_pm25 = generate_train_test_data(donggaocun_pm25_supervised, split_ratio=0.8, target_column='PM2.5')
    X_train_pm10, y_train_pm10, X_valid_pm10, y_valid_pm10 = generate_train_test_data(donggaocun_pm10_supervised, split_ratio=0.8, target_column='PM10')
    X_train_O3, y_train_O3, X_valid_O3, y_valid_O3 = generate_train_test_data(donggaocun_O3_supervised, split_ratio=0.8, target_column='O3')

    X_train_pm25.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/pm25_train_test/X_train_pm25.feather')
    y_train_pm25.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/pm25_train_test/y_train_pm25.feather')
    X_valid_pm25.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/pm25_train_test/X_valid_pm25.feather')
    y_valid_pm25.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/pm25_train_test/y_valid_pm25.feather')

    X_train_pm10.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/pm10_train_test/X_train_pm10.feather')
    y_train_pm10.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/pm10_train_test/y_train_pm10.feather')
    X_valid_pm10.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/pm10_train_test/X_valid_pm10.feather')
    y_valid_pm10.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/pm10_train_test/y_valid_pm10.feather')

    X_train_O3.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/O3_train_test/X_train_O3.feather')
    y_train_O3.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/O3_train_test/y_train_O3.feather')
    X_valid_O3.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/O3_train_test/X_valid_O3.feather')
    y_valid_O3.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/O3_train_test/y_valid_O3.feather')

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
