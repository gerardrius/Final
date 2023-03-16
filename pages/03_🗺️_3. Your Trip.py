# Basics
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

# Source functions
import src.cleaning as cleaning
import src.your_trip as trip

# Availability Predictions & Time Series
from prophet import Prophet
from datetime import datetime, timedelta

# Maps
import folium
from folium import Figure
from streamlit_folium import st_folium
import matplotlib.pyplot as plt


st.set_page_config(
    page_title = "Your Trip", 
    page_icon = "🗺️"
)

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

tab1, tab2 = st.tabs(['🚲 Your Trip', '🔮 Behind Predictions'])

# Introduction
tab1.title("Plan your Bike Trip!")

tab1.markdown('In this section, you will be able to get a detailed route from your actual location to your destination. The application provides the closest station to the start and end points with bike and free docks availability respectively. In addition, it provides the shortest path and a total time estimation for the whole trip.')
      

# User input
from_where = tab1.text_input('Where are you?')
to_where = tab1.text_input('Where do you want to go?')

time = tab1.select_slider('What time do you plan to start your trip?', dts)
index_of_time_list = dts.index(time) # important!!!

# Transform geographic input into coordinates

start = geolocator.geocode(from_where)
end = geolocator.geocode(to_where)

if start and end:
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

    tab1.text(f'Expected bike availability at {time}, at station {start_5["Station Name"].to_list()[0]} is: {round(start_clean_predictions[index_of_time_list]/start_station[1]*100 ,2)}%.')

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

    tab1.text(f'Expected free docks at {time}, at station {end_5["Station Name"].to_list()[0]} is: {round(end_clean_predictions[index_of_time_list]/start_station[1]*100 ,2)}%.')

    # Plot route
    import osmnx as ox
    import networkx as nx
    import plotly.graph_objects as go
    import taxicab as tc
    import math

    ox.config(log_console=True, use_cache=True)
    
    # Load the graph for New York City
    G = cleaning.get_graph_from_bbox (april)

    # MAP PLOT!!!
    # Walk 1
    start_walk_1 = geolocator.geocode(from_where) # Takes input FROM WHERE
    end_walk_1 = start_5.Coordinates.to_list()[0]

    # Bike Trip
    start_bike = start_5.Coordinates.to_list()[0]
    end_bike = end_5.Coordinates.to_list()[0]

    # Walk 2
    start_walk_2 = end_5.Coordinates.to_list()[0]
    end_walk_2 = geolocator.geocode(to_where) # Takes input TO WHERE

    # Coordinates of first and last point -> from Geopy
    start_walk_1 = (start_walk_1.latitude, start_walk_1.longitude)
    end_walk_2 = (end_walk_2.latitude, end_walk_2.longitude)

    # Get nodes for each point
    start_walk_1_node = ox.nearest_nodes(G, start_walk_1[1], start_walk_1[0])
    end_walk_1_node = ox.nearest_nodes(G, end_walk_1[1], end_walk_1[0])

    start_bike_node = end_walk_1_node
    end_bike_node = ox.nearest_nodes(G, end_bike[1], end_bike[0])

    start_walk_2 = end_bike_node
    end_walk_2 = ox.nearest_nodes(G, end_walk_2[1], end_walk_2[0])

    # Routes
    walk_1 = nx.shortest_path(G, start_walk_1_node, end_walk_1_node, weight='length')
    bike_route = nx.shortest_path(G, start_bike_node, end_bike_node, weight='length')
    walk_2 = nx.shortest_path(G, start_walk_2, end_walk_2, weight='length')

    # Journey plot
    rc1 = ['r'] * (len(walk_1) - 1)
    rc2 = ['b'] * len(bike_route)
    rc3 = ['r'] * (len(walk_2) -1)
    rc = rc1 + rc2 + rc3
    nc = ['r', 'r', 'b', 'b', 'r', 'r']
    fig, ax = ox.plot_graph_routes(G, [walk_1, bike_route, walk_2], route_color = rc, node_size=0)

    with tab1:
        st.pyplot(fig)

    walk_1_distance_time = trip.walk_distance_time(start_walk_1, end_walk_1, G)
    walk_2_distance_time = trip.walk_distance_time(start_walk_2, end_walk_2, G)

    bike_trip_distance_time = trip.bike_distance_time (start_bike, end_bike, G)

    total_time = walk_1_distance_time[1] + bike_trip_distance_time[1] + walk_2_distance_time[1]

    total_distance = walk_1_distance_time[0] + bike_trip_distance_time[0] + walk_2_distance_time[0]
    tab1.markdown(f'**Distance**: {total_distance} meters,  divided in a {walk_1_distance_time[0] + walk_2_distance_time[0]}m walk and a {bike_trip_distance_time[0]}m ride.')   
    tab1.markdown(f"**Expected duration**: {total_time} minutes, divided in a {walk_1_distance_time[1] + walk_2_distance_time[1]}' walk and a {bike_trip_distance_time[1]}' ride.")


# TAB 2 -> Behind Predictions.

tab2.header('Prediction System Explanation')

tab2.markdown('As mentioned in the main page of the app, one of the biggest challenges of the project has been the predictive analysis of NYC Citi Bike System. The available data contained only _human trips_, whereas further bike mobility was not taken into consideration (e.g. bike relocation, maintenance, etc.).')

tab2.markdown('In fact, _truck mobility_ was extremely important to get an accurate picture of the exact position of each bike, which is identified by its unique Bike ID, at each time. Only by having this information, it is possible to figure out the number of bikes and free docks in each Station at any time point, as well as the maximum station capacity, which can be assumed to be the maximum number of bikes recorded in a station during the whole time period.')

tab2.markdown('Consequently, to solve this puzzle, I created a parallel dataframe containing all _non-human trips_. Each _truck trip_ was obtained by checking if a unique Bike ID did not start a trip in the same station where it ended the previous one. If this was the case, it meant that an instance of a _non-human trip_ took place, so it was appended to the parallel dataframe. Once all trips of both kinds were recorded, their corresponding dataframes were merged and the enigma was solved!')

tab2.subheader('Obtention of a Station Availability Time Series')

# Example distribution along the month

tab2.markdown('The Time Series below shows the evolution of availability across time in an example station; an essential step to predict future availability. Dark blue area stands for bike availability percentage while light blue represents free docks proportion.')
fig_example = trip.station_example_function (ALL_TRIPS)
tab2.plotly_chart(fig_example)

# Model plot forecast

tab2.subheader('Prophet Model Application') 

tab2.markdown("From Station Availability Time Series, a Prophet Model was trained to get the future prediction of bikes and free docks availability in a given station (usually the closest stations to user's initial location and destination respectively). Below there is the example station model and its next 24h prediction:")

model_plot = Image.open('pages/images/model_plot.png')

tab2.image(model_plot, caption = 'Model Plot with 24h Availability Forecast.')

# Model Components
tab2.markdown('Last but not least, model components provide an interesting picture and a valuable insight of the availability prediction over the studied time period, tackling overall trend, weekly and daily.')

model_components = Image.open('pages/images/model_components.png')

tab2.image(model_components, caption = 'Model Components divided by trend, weekly and daily.')
