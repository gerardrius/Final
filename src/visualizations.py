    # Libraries
import pandas as pd
import numpy as np

# For maps
import folium.plugins
from folium import Figure
from folium.plugins import HeatMapWithTime

# Graph Visualizations
import seaborn as sns
import matplotlib.pyplot as plt
import folium
import plotly.express as px

# Map visualizations
import folium.plugins
from folium import Figure
from folium.plugins import HeatMapWithTime



    # TRIP
# Duration distribution
def duration_distribution (df):
    counts, bins = np.histogram(df.duration, bins=range(30, 3600, 60))
    bins = 0.5 * (bins[:-1] + bins[1:])
    fig = px.bar(x=bins, y=counts, labels={'x':'Duration (in seconds)', 'y':'Frequency'}, color_discrete_sequence =['darkblue']*len(df), title = 'Trip Duration Distribution')
    return fig

# Displacement distribution
def displacement_distribution (df):
    counts, bins = np.histogram(df.distance, bins=range(50, 5000, 100))
    bins = 0.5 * (bins[:-1] + bins[1:])
    fig = px.bar(x=bins, y=counts, labels={'x':'Displacement (in meters)', 'y':'Frequency'}, color_discrete_sequence =['darkblue']*len(df), title = 'Trip Displacement Distribution')
    return fig

# Average pace
def average_pace_distribution (df):
    avg_pace_df = df
    average_pace = []
    for i, row in df.iterrows():
        average_pace.append(row['distance'] / row['duration'] * 3.6)
    
    avg_pace_df['average_pace'] = average_pace

    counts, bins = np.histogram(avg_pace_df.average_pace, bins=range(1, 20, 1))
    bins = 0.5 * (bins[:-1] + bins[1:])

    fig = px.bar(x=bins, y=counts, labels={'x':'Average Pace (in km/h)', 'y':'Frequency'}, color_discrete_sequence =['darkblue']*len(df), title = 'Trip Average Pace Distribution')
    return fig

# Trips monthly
def monthly_trips (df):
    month_df = df
    trip = [1]*month_df.shape[0]
    month_df['trip_sum'] = trip
    grouped_by_date = month_df[['trip_date', 'trip_sum']].groupby(by = ['trip_date']).sum().reset_index(drop=False)

    plot_df = grouped_by_date
    fig = px.area(plot_df, x='trip_date', y='trip_sum', labels={'trip_date':'Trip Date', 'trip_sum':'Number of Trips'}, color_discrete_sequence =['darkblue']*len(df), title = 'Trip Time Series')
    return fig

# Trips by day
def trips_by_day (df):
    fig = px.histogram(df, x='weekday', range_y=(80000, 110000), labels={'count':'Total of occurrences', 'weekday':'Weekday'}, color_discrete_sequence =['darkblue']*len(df), title = 'Trips by Weekday')
    return fig

# Trips by hours
def trips_by_hour (df):
    fig = px.histogram(df, x='start_hour', labels={'count':'Total of occurrences', 'start_hour':'Hour'}, color_discrete_sequence =['darkblue']*len(df), title = 'Trips by Hour')
    fig.update_layout(bargap = 0.06)
    return fig



    # STATION
# Heatmap with hourly activity
def heatmapWithTime (df, day):
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

# Starts distribution
def starts_distribution (df):
    figure4 = Figure(width=850,height=550)
    new_york4 = folium.Map(location=[40.7230679, -73.974965513],zoom_start=13)

    folium.TileLayer('cartodbpositron').add_to(new_york4)
    figure4.add_child(new_york4)

    grouped_df = df[['start_station_name', 'start_lat', 'start_lng', 'duration', 'start_hour']].groupby(by=['start_station_name']).mean().reset_index()
    grouped_df['am_pm'] = grouped_df['start_hour'].apply(lambda x: 'AM' if x < 14 else 'PM')

    for i, row in grouped_df.iterrows():

        marker = {'location': [row['start_lat'], row['start_lng']], 'tooltip': 'Citi Bike Station'}

        if row['am_pm'] == 'AM':
            icon = folium.Icon(color='lightblue', icon='')

        elif row['am_pm'] == 'PM':
            icon = folium.Icon(color='darkblue', icon='')

        new_marker = folium.Marker(**marker, icon = icon, radius = 2)

        new_marker.add_to(new_york4)

    return figure4

def ends_distribution (df):
    figure5 = Figure(width=850,height=550)
    new_york5 = folium.Map(location=[40.7230679, -73.974965513],zoom_start=13)

    folium.TileLayer('cartodbpositron').add_to(new_york5)
    figure5.add_child(new_york5)

    grouped_df = df[['end_station_name', 'end_lat', 'end_lng', 'duration', 'start_hour']].groupby(by=['end_station_name']).mean().reset_index()
    grouped_df['am_pm'] = grouped_df['start_hour'].apply(lambda x: 'AM' if x < 14 else 'PM')

    for i, row in grouped_df.iterrows():

        marker = {'location': [row['end_lat'], row['end_lng']], 'tooltip': 'Citi Bike Station'}

        if row['am_pm'] == 'AM':
            icon = folium.Icon(color='lightblue', icon='')

        elif row['am_pm'] == 'PM':
            icon = folium.Icon(color='darkblue', icon='')

        new_marker = folium.Marker(**marker, icon = icon, radius = 2)

        new_marker.add_to(new_york5)

    return figure5


    # DEMOGRAPHICS
# Age distribution (by gender, not by user type since customers do not set neither gender nor age)
def age_distribution (df):
    age_gender = df[(df['gender'] == 1) | (df['gender'] == 2)]
    age_gender['gender'] = age_gender['gender'].apply(lambda x: 'Male' if x == 1 else 'Female')

    years_list = [str(i) for i in range(1940, 1998)]

    age_gender['birth_year'] = age_gender['birth_year'].apply(lambda x: int(x) if x in years_list else np.nan)
    age_gender = age_gender.groupby(['gender', 'birth_year']).size().to_frame()
    age_gender = age_gender.reset_index()
    age_gender.rename(columns={0: 'count'}, inplace = True)

    fig = px.area(age_gender, 
        x='birth_year',
        y= 'count',
        color = 'gender',
        labels={'birth_year': 'Birth Year', 'count': 'Number of Users'},
        color_discrete_map = {'Male': 'blue', 'Female': 'darkblue'}, 
        title = 'User Age Distribution')
    return fig

# Gender distribution
def gender_distribution (df, day):
    gender = df[df['weekday'] == day]
    gender = gender[(gender['gender'] == 1) | (gender['gender'] == 2)]
    gender['gender'] = gender['gender'].apply(lambda x: 'Male' if x == 1 else 'Female')
    gender['val'] = [1]*gender.shape[0]

    figure_gender = px.pie(gender, values = 'val', names = 'gender', color = 'gender', color_discrete_map={'Male':'blue', 'Female':'darkblue'})
    figure_gender.update_traces(textposition='inside', textinfo='percent+label')
    return figure_gender

# User type distribution
def user_type (df, day):
    user_df = df[df['weekday'] == day]
    user_df['val'] = [1]*user_df.shape[0]

    figure_member = px.pie(user_df, values = 'val', names = 'member_casual', color = 'member_casual', color_discrete_map={'Subscriber':'blue', 'Customer':'darkblue'})
    figure_member.update_traces(textposition='inside', textinfo='percent+label')
    return figure_member

# Number and percentage of users having not defined neither age nor gender
def age_not_defined (df):
    # This code provides the number of not defined ages.
    absolute_number = df[df['birth_year'] == '\\N'].shape[0]
    relative_number = absolute_number / df.shape[0]
    return (absolute_number, relative_number)

def gender_not_defined (df):
    absolute_number = df[df['gender'] == 0].shape[0]
    relative_number = absolute_number /df.shape[0]
    return (absolute_number, relative_number)



# Get all stations
def get_all_stations (df):
    all_start = df['start_station_name'].unique().tolist()
    all_end = df['end_station_name'].unique().tolist()
    all_start.extend(all_end)
    return list(set(all_start))