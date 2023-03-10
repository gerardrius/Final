    # Libraries
import pandas as pd

# For maps
import folium.plugins
from folium import Figure
from folium.plugins import HeatMapWithTime




    # Trip


    # Station
# Heatmap with hourly activity
def testfunct (df, day):
    test_map_viz = df[['start_hour', 'started_at', 'bike_id', 'start_lat', 'start_lng', 'weekday']]
    test_map_viz = test_map_viz[test_map_viz['weekday'] == day]

    lat_lng_list = []
    for i in range(24):
        temp=[]
        for index, row in test_map_viz[test_map_viz['start_hour'] == i].iterrows():
            temp.append([row['start_lat'],row['start_lng']])
        lat_lng_list.append(temp)

    figure1 = Figure(width=850,height=550)
    new_york1 = folium.Map(location=[40.712776, -74.005974],zoom_start=12)

    figure1.add_child(new_york1)
    folium.TileLayer('cartodbpositron').add_to(new_york1)
    gradient = {.33: 'white', .66: 'lightblue', 1: 'blue'}

    HeatMapWithTime(lat_lng_list, radius=5, auto_play=True, position='bottomright', gradient=gradient).add_to(new_york1)

    return figure1


# Stations with more starts
def top_n_starts (df, n):
    top_n = df['start_station_name'].value_counts()[:n].to_frame().reset_index()
    new_index = [i for i in range(1, len(top_n) + 1)]
    top_n['new_index'] = new_index

    top_n.set_index('new_index', drop=True, inplace=True)
    top_n.index.rename('Classification', inplace = True)

    top_n.rename(columns={'index': 'Start Station Name', 'start_station_name': 'Number of Starts'}, inplace = True)
    return top_n

# Stations with more ends
def top_n_ends (df, n):
    top_n = df['end_station_name'].value_counts()[:n].to_frame().reset_index()
    top_n.rename(columns={'index': 'End Station Name', 'end_station_name': 'Number of Ends'}, inplace = True)


    top_n = df['end_station_name'].value_counts()[:n].to_frame().reset_index()
    new_index = [i for i in range(1, len(top_n) + 1)]
    top_n['new_index'] = new_index

    top_n.set_index('new_index', drop=True, inplace=True)
    top_n.index.rename('Classification', inplace = True)

    top_n.rename(columns={'index': 'End Station Name', 'end_station_name': 'Number of Ends'}, inplace = True)
    return top_n

# Most busy stations overall
def top_busy_stations (df, n):
    start = df.start_station_name.value_counts().to_frame().reset_index().sort_values(by=['index'])
    end = df.end_station_name.value_counts().to_frame().reset_index().sort_values(by=['index'])
    busy_stations = start.merge(end, how='outer', on='index')

    total_activity = []
    for i, row in busy_stations.iterrows():
        total_activity.append(row['start_station_name'] + row['end_station_name'])

    busy_stations['total_activity'] = total_activity
    busy_stations.sort_values(by = 'total_activity', ascending=False, inplace = True)
    busy_stations.reset_index(inplace=True, drop=True)
    busy_stations.rename(columns={'index': 'Station Name', 'start_station_name': 'Trips Started', 'end_station_name': 'Trips Ended','total_activity': 'Total Activity'}, inplace = True)

    new_index = [i for i in range (1, len(busy_stations) + 1)]
    busy_stations['new_index'] = new_index

    busy_stations.set_index('new_index', drop=True, inplace=True)
    busy_stations.index.rename('Classification', inplace = True)

    return busy_stations[:n]

# Your station
def your_station_data (df, station_name):
    start = df.start_station_name.value_counts().to_frame().reset_index().sort_values(by=['index'])
    end = df.end_station_name.value_counts().to_frame().reset_index().sort_values(by=['index'])
    busy_stations = start.merge(end, how='outer', on='index')

    all_instances = busy_stations.shape[0]

    all_stations_activity = top_busy_stations (df, all_instances)

    return all_stations_activity[all_stations_activity['Station Name'] == station_name]

# 

    # Demographics
