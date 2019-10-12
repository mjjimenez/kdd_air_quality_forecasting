# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
import os
import pickle
from xgboost import XGBRegressor

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 

    X_train_pm25 = pd.read_feather(f'{input_filepath}/pm25_train_test/X_train_pm25.feather')
    y_train_pm25 = pd.read_feather(f'{input_filepath}/pm25_train_test/y_train_pm25.feather')

    pm25_xg_model = XGBRegressor(n_estimators=500, learning_rate=0.01, max_depth=2)
    pm25_xg_model.fit(X_train_pm25, y_train_pm25)

    pickle.dump(pm25_xg_model, open(f'{output_filepath}/pm25_xgb_model.pickle.dat')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
