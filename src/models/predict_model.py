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
import math

def rmse(x,y): return math.sqrt(((x-y)**2).mean())


def score(m, X_train, y_train, X_valid, y_valid):
    res = [rmse(m.predict(X_train), y_train), rmse(m.predict(X_valid), y_valid),
                m.score(X_train, y_train), m.score(X_valid, y_valid)]
    if hasattr(m, 'oob_score_'): res.append(m.oob_score_)
    return res


def smape(predicted, actual):
    dividend= np.abs(np.array(actual) - np.array(predicted))
    denominator = np.array(actual) + np.array(predicted)

    return 2 * np.mean(np.divide(dividend, denominator, out=np.zeros_like(dividend), where=denominator!=0, casting='unsafe'))


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 

    X_train = pd.read_feather(f'{input_filepath}/pm25_train_test/X_train_pm25.feather').set_index('utc_datetime')
    y_train = pd.read_feather(f'{input_filepath}/pm25_train_test/y_train_pm25.feather').set_index('utc_datetime')

    X_valid = pd.read_feather(f'{input_filepath}/pm25_train_test/X_valid_pm25.feather').set_index('utc_datetime')
    y_valid = pd.read_feather(f'{input_filepath}/pm25_train_test/y_valid_pm25.feather').set_index('utc_datetime')

    pm25_xg_model = pickle.load(open('models/pm25_xgb_model.pickle.dat', 'rb'))
    
    _, rmse_valid, _, _ = score(pm25_xg_model, X_train, y_train.values, X_valid, y_valid.values)
    print(f'RMSE score PM2.5 for validation set: {rmse_valid}')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
