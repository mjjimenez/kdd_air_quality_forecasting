# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
from fancyimpute import KNN
from fancyimpute import IterativeImputer


def impute_values(df, imputer=None, columns_to_impute=None):

    if imputer and (columns_to_impute is not None):
            df_remaining = df.drop(columns_to_impute, axis=1)
            df_to_impute = df[columns_to_impute]
            imputed_values = imputer.fit_transform(df_to_impute)
            df_imputed = pd.DataFrame(imputed_values, columns=columns_to_impute, index=df_remaining.index)
            df = pd.concat([df_remaining, df_imputed], axis=1)
    return df



@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 
    
    donggaocun_df = pd.read_feather(f'{input_filepath}/donggaocun_aq_merged_weather.feather')
    columns_to_impute = donggaocun_df.columns[donggaocun_df.columns.str.contains('meo|grid')]
    columns_to_impute = columns_to_impute[~columns_to_impute.str.contains('weather')]
    imputed_df = impute_values(donggaocun_df, KNN(5), columns_to_impute)
    imputed_df.to_feather(f'{output_filepath}/donggaocun_processed.feather')

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
