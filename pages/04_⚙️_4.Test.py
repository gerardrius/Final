# Basics
import streamlit as st
import pandas as pd
import numpy as np
import src.cleaning as cleaning
import src.your_trip as trip
from prophet import Prophet

import folium
from folium import Figure
from streamlit_folium import st_folium

from datetime import datetime, timedelta

def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta

dts = [dt.strftime('%H:%M') for dt in 
       datetime_range(datetime(2014, 4, 1, 0), datetime(2014, 4, 2, 0), 
       timedelta(minutes=15))]

from geopy.geocoders import Nominatim

april = pd.read_csv('data/april_2014.csv')
ALL_TRIPS = pd.read_csv('data/all_trips.csv')

geolocator = Nominatim(user_agent="my_app")

tab1, tab2, tab3 = st.tabs(['🚲 Your Trip' , '📈 Further Availability Information', '🔮 Behind Predictions'])

# User input
from_where = tab1.text_input('Where are you?')
to_where = tab1.text_input('Where do you want to go?')

time = tab1.select_slider('What time do you plan to start your trip?', dts)
index_of_time_list = dts.index(time) # important!!!

# Transform geographic input into coordinates

start = geolocator.geocode(from_where)
end = geolocator.geocode(to_where)

start_point = (start.latitude, start.longitude)
end_point = (end.latitude, end.longitude)

# This is to get information on distances depending on users input
from geopy.geocoders import Nominatim
import geopy.distance

geolocator = Nominatim(user_agent="my_app")

# We have stations coordinates
stations_coordinates = cleaning.stations_coordinates(april)
stations_coordinates = cleaning.geo_points_stations (stations_coordinates)

# Lists with distances from start and end points to closest stations
distance_to_start = []
for i, row in stations_coordinates.iterrows():
    distance_to_start.append(geopy.distance.distance(start_point, row['coordinates']).m)
stations_coordinates['distance_to_start'] = distance_to_start

distance_to_end = []
for i, row in stations_coordinates.iterrows():
    distance_to_end.append(geopy.distance.distance(end_point, row['coordinates']).m)
stations_coordinates['distance_to_end'] = distance_to_end

# Dataframes with 5 closest stations to start and end points
start_5 = stations_coordinates[['station_name', 'station_id', 'coordinates', 'distance_to_start']].sort_values(by=['distance_to_start'], ascending=True).iloc[:5].reset_index(drop=True)
end_5 = stations_coordinates[['station_name', 'station_id', 'coordinates', 'distance_to_end']].sort_values(by=['distance_to_end'], ascending=True).iloc[:5].reset_index(drop=True)

start_5 = start_5.rename(columns={'station_name': 'Station Name', 'station_id': 'Station ID', 'coordinates': 'Coordinates', 'distance_to_start': 'Distance (in m)'})
end_5 = end_5.rename(columns={'station_name': 'Station Name', 'station_id': 'Station ID', 'coordinates': 'Coordinates', 'distance_to_end': 'Distance (in m)'})

# Predictive part for start
closest_start_id = start_5['Station ID'].to_list()[0]

start_station = trip.station_load_time_series (ALL_TRIPS, closest_start_id)
bike_availability = start_station[0]['bikes_in_station'].to_list()
time_range = trip.time_range
start_time_series_df = pd.DataFrame({'time': time_range[:-1], 'bikes_available': bike_availability[:-1]})
start_time_series_df['time'] = pd.to_datetime(start_time_series_df['time'], infer_datetime_format = True)
start_time_series_df['docks_available'] = [start_station[1]]*start_time_series_df.shape[0] - start_time_series_df['bikes_available']

start_model = Prophet()
start_data = start_time_series_df[['time', 'bikes_available']]
start_data = start_data.rename(columns = {'time': 'ds', 'bikes_available': 'y'})
start_model.fit(start_data)
start_future = start_model.make_future_dataframe(periods=96, freq='15min')
start_forecast = start_model.predict(start_future)
start_predictions = start_forecast['yhat'].tail(96).values
start_clean_predictions = []
for prediction in start_predictions:
    start_clean_predictions.append(round(prediction))

tab1.text(f'Bike availability at station {start_5["Station Name"].to_list()[0]} is {round(start_clean_predictions[index_of_time_list]/start_station[1]*100 ,2)}%.')

# Predictive part for end
closest_end_id = end_5['Station ID'].to_list()[0]

end_station = trip.station_load_time_series (ALL_TRIPS, closest_end_id)
bike_availability = end_station[0]['bikes_in_station'].to_list()
time_range = trip.time_range
end_time_series_df = pd.DataFrame({'time': time_range[:-1], 'bikes_available': bike_availability[:-1]})
end_time_series_df['time'] = pd.to_datetime(end_time_series_df['time'], infer_datetime_format = True)
end_time_series_df['docks_available'] = [end_station[1]]*end_time_series_df.shape[0] - end_time_series_df['bikes_available']

end_model = Prophet()
end_data = end_time_series_df[['time', 'docks_available']]
end_data = end_data.rename(columns = {'time': 'ds', 'docks_available': 'y'})
end_model.fit(end_data)
end_future = end_model.make_future_dataframe(periods=96, freq='15min')
end_forecast = end_model.predict(end_future)
end_predictions = end_forecast['yhat'].tail(96).values
end_clean_predictions = []
for prediction in end_predictions:
    end_clean_predictions.append(round(prediction))

tab1.text(f'Bike availability at station {end_5["Station Name"].to_list()[0]} is {round(end_clean_predictions[index_of_time_list]/start_station[1]*100 ,2)}%.')

G = cleaning.get_graph_from_bbox (april)







