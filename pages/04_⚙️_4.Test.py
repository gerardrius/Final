# Basics
import streamlit as st
import pandas as pd
import numpy as np
import src.cleaning as cleaning

import folium
from folium import Figure
from streamlit_folium import st_folium

from geopy.geocoders import Nominatim

april = pd.read_csv('data/april_2014.csv')

geolocator = Nominatim(user_agent="my_app")

from_where = st.text_input('Where are you?')
to_where = st.text_input('Where do you want to go?')

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

st.markdown(f'5 closest stations from **{from_where}**:')

st.dataframe(start_5)



# Map with plotted station points:
figure15 = Figure(width=850,height=550)
new_york15 = folium.Map(location=[40.7230679, -73.974965513],zoom_start=13)

folium.TileLayer('cartodbpositron').add_to(new_york15)
figure15.add_child(new_york15)


for i, row in start_5.iterrows():

    marker = {'location': row['Coordinates'], 'tooltip': 'Citi Bike Station'}

    icon = folium.Icon(color='lightblue', icon='')

    new_marker = folium.Marker(**marker, icon = icon, radius = 2)

    new_marker.add_to(new_york15)

for i, row in end_5.iterrows():

    marker = {'location': row['Coordinates'], 'tooltip': 'Citi Bike Station'}

    icon = folium.Icon(color='darkblue', icon='')

    new_marker = folium.Marker(**marker, icon = icon, radius = 2)

    new_marker.add_to(new_york15)

st_map = st_folium(figure15, width = 850)

st.markdown(f'5 closest stations from **{to_where}**:')

st.dataframe(end_5)