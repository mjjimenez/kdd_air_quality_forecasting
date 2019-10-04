# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import itertools
import os

def process_weather_station_data(df, station_name):
    """
    Rename weather station data so each station's weather data can be distinguished.
    Selects only weather features to include in the dataframe.
    """
    df = df.iloc[:, 3:].copy()
    new_names = [(i,f"{station_name}_{i}") for i in df.iloc[:, 1:].columns.values]
    return df.rename(columns = dict(new_names))

def output_nn_weather_data(aq_station, latitude, longitude, nn_model, weather_stations, weather_data):

    nn_result = nn_model.kneighbors([[latitude, longitude]], return_distance=False)

    nn_index = nn_result[0]
    nn_station_names = weather_stations.iloc[nn_index].station_id

    weather_data_dfs = [weather_data[weather_data.station_id == weather_station_id] for weather_station_id in nn_station_names]
    weather_data_dfs = [process_weather_station_data(df, station_name) for station_name, df in zip(nn_station_names, weather_data_dfs)]

    return weather_data_dfs


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """ 

    # Create directory to save merged air quality and weather data

    os.makedirs(f'{output_filepath}', exist_ok=True)

    # Load beijing air quality, grid and observed weather stations.

    beijing_aq_stations = pd.read_feather(f'{input_filepath}/beijing_aq_stations.feather')

    grid_weather_stations = pd.read_feather(f'{input_filepath}/Beijing_grid_weather_station.feather')
    grid_weather_data = pd.read_feather(f'{input_filepath}/beijing_meo_grid.feather')

    observed_weather_stations = pd.read_feather(f'{input_filepath}/beijing_meo_observed_stations.feather')
    observed_weather_data = pd.read_feather(f'{input_filepath}/beijing_meo_observed_union.feather')

    beijing_aq_data = pd.read_feather(f'{input_filepath}/beijing_aq_union.feather')

    ## Fit NearestNeighbor model to grid and observed weather station's coordinates

    grid_nn_model = NearestNeighbors(n_neighbors=2, metric='haversine', n_jobs=-1)
    grid_nn_model.fit(grid_weather_stations.set_index('station_id'))

    observed_nn_model = NearestNeighbors(n_neighbors=1, metric='haversine', n_jobs=-1)
    observed_nn_model.fit(observed_weather_stations.set_index('station_id'))

    # Iterate through each air quality station
    for index, aq_station_info in beijing_aq_stations.iterrows():

        # Fetch KNN grid station weather data

        nn_grid_weather_data = output_nn_weather_data(aq_station_info['station_id'],
                                                      aq_station_info['latitude'],
                                                      aq_station_info['longitude'],
                                                      grid_nn_model,
                                                      grid_weather_stations,
                                                      grid_weather_data)

        # Fetch KNN observed station weather data

        nn_observed_weather_data = output_nn_weather_data(aq_station_info['station_id'],
                                                         aq_station_info['latitude'],
                                                         aq_station_info['longitude'],
                                                         observed_nn_model,
                                                         observed_weather_stations,
                                                         observed_weather_data)


        # Merge to air station air quality data
        station_aq_data = beijing_aq_data[beijing_aq_data.station_id == aq_station_info['station_id']]

        for weather_df in itertools.chain(nn_grid_weather_data, nn_observed_weather_data):
            station_aq_data = station_aq_data.merge(weather_df, on='utc_datetime', how='inner')


        # Fill-in missing hourly values to impute later.
        date_range_index = pd.date_range(start=station_aq_data.utc_datetime.min(), end=station_aq_data.utc_datetime.max(), freq='H')
        station_aq_data = station_aq_data.set_index('utc_datetime').reindex(date_range_index)

        # TODO: Add imputation method here

        # Save to interim feather file
        station_aq_data = station_aq_data.drop('station_id', axis=1).reset_index().rename(columns={'index': 'utc_datetime'})
        station_name = aq_station_info['station_id']
        station_aq_data.to_feather(f'{output_filepath}/{station_name}_merged_weather.feather')


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
