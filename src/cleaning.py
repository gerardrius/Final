import pandas as pd
import numpy as np

# Trip distance
import geopy.distance

# Trip duration
import datetime
from datetime import datetime

# Trip distance
import osmnx as ox
from osmnx import graph_from_bbox
import networkx as nx
import taxicab as tc
from shapely.geometry import Point, LineString

# 2014
def rename_columns (df):
    df.rename(columns={
        'tripduration': 'duration','starttime': 'started_at', 'stoptime': 'ended_at', 'start station id': 'start_station_id',
        'start station name': 'start_station_name', 'start station latitude': 'start_lat', 
        'start station longitude': 'start_lng', 'end station id': 'end_station_id', 'end station name': 'end_station_name', 
        'end station latitude': 'end_lat', 'end station longitude': 'end_lng', 'bikeid': 'bike_id', 'usertype': 'member_casual', 
        'birth year': 'birth_year', 'gender': 'gender'}, inplace = True)
    return df

# Scalable
def trip_distance (df):
    distance_list = []

    for index, row in df.iterrows():
        lat0 = row['start_lat']
        lng0 = row['start_lng']
        lat1 = row['end_lat']
        lng1 = row['end_lng']

        try:
            distance_ = geopy.distance.distance((lat0, lng0), (lat1, lng1)).m
            distance_list.append(round(distance_, 2))
        except:
            distance_list.append(np.nan)
            
    df['distance'] = distance_list
    
    return df

def get_hour (df):
    start_hour_list = []
    end_hour_list = []
    for i, row in df.iterrows():
        start_hour = row['started_at'][-8:-6]
        end_hour = row['ended_at'][-8:-6]

        try:
            start_hour_list.append(int(start_hour))
            end_hour_list.append(int(end_hour))
        except:
            start_hour_list.append(np.nan)
            end_hour_list.append(np.nan)

    df['start_hour'] = start_hour_list
    df['end_hour'] = end_hour_list

    return df

def get_date (df):
    datetime_objects_list = []
    for i, row in df.iterrows():
        datetime_obj = datetime.strptime(row['started_at'][:10], '%Y-%m-%d')
        datetime_objects_list.append(datetime_obj)

    df['trip_date'] = datetime_objects_list
    return df

def datetime_format (df):
    started_at = []
    ended_at = []
    for i, row in df.iterrows():
        started_at_datetime = datetime.strptime(row['started_at'], '%Y-%m-%d %H:%M:%S')
        ended_at_datetime = datetime.strptime(row['ended_at'], '%Y-%m-%d %H:%M:%S')

        try:
            started_at.append(started_at_datetime)
            ended_at.append(ended_at_datetime)
        except:
            started_at.append(np.nan)
            ended_at.append(np.nan)

    df['started_at'] = started_at
    df['ended_at'] = ended_at
    return df

def get_categorical_date (df):
    weekday_list = []
    month_list = []

    for i, row in df.iterrows():
        weekday = row['started_at'].strftime('%A')
        month = row['ended_at'].strftime('%B')

        try:
            weekday_list.append(weekday)
            month_list.append(month)
        except:
            weekday_list.append(np.nan)
            month_list.append(np.nan)           
    
    df['weekday'] = weekday_list
    df['month'] = month_list

    return df

def is_weekend (df):
    df['weekend'] = df['weekday'].apply(lambda x: 1 if x in ['Saturday', 'Sunday'] else 0)
    return df

def get_real_distance (df):

    max_start_lat, max_end_lat = df.start_lat.max(), df.end_lat.max()
    max_start_lng, max_end_lng = df.start_lng.max(), df.end_lng.max()

    min_start_lat, min_end_lat = df.start_lat.min(), df.end_lat.min()
    min_start_lng, min_end_lng = df.start_lng.min(), df.end_lng.min()

    ymax = max(max_start_lat, max_end_lat)
    xmax = max(max_start_lng, max_end_lng)
    ymin = min(min_start_lat, min_end_lat)
    xmin = min(min_start_lng, min_end_lng)

    G = graph_from_bbox(ymax, ymin, xmin, xmax, network_type='drive', simplify=True)

    real_distance_list = []
    for i, row in df.iterrows():
        orig = (row['start_lat'], row['start_lng'])
        dest = (row['end_lat'], row['end_lng'])
        try:
            route = tc.distance.shortest_path(G, orig, dest)
            real_distance_list.append(route[0])
        except:
            real_distance_list.append(np.nan)

    df['real_distance'] = real_distance_list

    return df

# 2022
def trip_duration (df):
    duration_list = []
    for i, row in df.iterrows():
        start_time = datetime.strptime(row['started_at'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(row['ended_at'], '%Y-%m-%d %H:%M:%S')

        try:
            duration = (end_time - start_time).seconds
            duration_list.append(duration)
        except:
            duration_list.append(np.nan)


    df['duration'] = duration_list

    return df