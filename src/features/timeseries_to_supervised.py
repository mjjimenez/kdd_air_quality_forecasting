# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np

def timeseries_to_supervised(df, lag=1, dropnan=True):

    df = pd.DataFrame(df)
    columns = [df.shift(i).rename(columns=lambda x: f"{x}(-{i})") for i in range(1, lag+1)]
    columns.insert(0, df)
    df = pd.concat(columns, axis=1)

    if dropnan:
        df.dropna(inplace=True)
    else:
        df = df[lag:] #skip nan at the start
        df.fillna(-1, inplace=True)

    return df


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 
    
    donggaocun_aq = pd.read_feather(f'{input_filepath}/donggaocun_processed.feather')
    donggaocun_aq = donggaocun_aq.set_index('utc_datetime')
    
    pm25_supervised_df = timeseries_to_supervised(donggaocun_aq, 16, dropnan=False)
    pm10_supervised_df = timeseries_to_supervised(donggaocun_aq, 15, dropnan=False)
    O3_supervised_df = timeseries_to_supervised(donggaocun_aq, 10, dropnan=False)

    pm25_supervised_df.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/donggaocun_aq_pm25_supervised_df.feather')
    pm10_supervised_df.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/donggaocun_aq_pm10_supervised_df.feather')
    O3_supervised_df.reset_index().rename(columns={'index': 'utc_datetime'}).to_feather(f'{output_filepath}/donggaocun_aq_O3_supervised_df.feather')
    

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
