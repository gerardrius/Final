import pandas as pd
import numpy as np

import datetime
from datetime import datetime, timedelta
import taxicab as tc
import math
import osmnx as ox
import networkx as nx

def time_difference (df):
    df['started_at'] = pd.to_datetime(df['started_at'], infer_datetime_format = True)
    df['ended_at'] = pd.to_datetime(df['ended_at'], infer_datetime_format = True)
    return df

def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta
        
time_range = [dt.strftime('%Y-%m-%d T%H:%M') for dt in 
    datetime_range(datetime(2014, 4, 1, 0), datetime(2014, 5, 1, 0, 5), 
    timedelta(minutes=15))]

def rounder (num):
    if num <= 20:
        return 20
    else:
        if round(num, -1) >= num:
            return round(num, -1)
        else:
            return round(num, -1) + 10
        
def time_difference (df):
    df['started_at'] = pd.to_datetime(df['started_at'], infer_datetime_format = True)
    df['ended_at'] = pd.to_datetime(df['ended_at'], infer_datetime_format = True)
    return df

def station_load_time_series (df, id):
    id_starts = []
    id_ends = []

    df = time_difference (df)

    for date in time_range:
        date_time_obj = datetime.strptime(date, '%Y-%m-%d T%H:%M')

        ends = df[(df['ended_at'] <= date_time_obj) & (df['last_end'] == id)].last_end.value_counts().to_frame().reset_index().rename(columns = {'index': 'id', 'last_end': 'counts'})
        starts = df[(df['started_at'] <= date_time_obj)& (df['next_start'] == id)].next_start.value_counts().to_frame().reset_index().rename(columns = {'index': 'id', 'next_start': 'counts'})
        
        try:
            id_starts.append(starts.iloc[0]['counts'])
            id_ends.append(ends.iloc[0]['counts'])
        except:
            id_starts.append(0)
            id_ends.append(0)

    station_load = pd.DataFrame({'ends': id_ends, 'starts': id_starts})
    station_load['bikes_in_station'] = station_load['ends'] - station_load['starts']

    station_capacity = rounder(max(station_load['bikes_in_station']))

    return station_load, station_capacity

def walk_distance_time (start, end, G):
    try:
        route = tc.distance.shortest_path(G, start, end)
        return round(route[0], 2), math.ceil((route[0])/100) # Average walk pace assumed -> 1' for every 100m
    except:
        return 0, 0
    
def bike_distance_time (start, end, G):
    try:
        route = tc.distance.shortest_path(G, start, end)
        return round(route[0], 2), math.ceil((route[0])/(3.3*60)) # Assuming real pace is slightly greater than displacement pace, 2.5 -> 3.3
    except:
        return 0, 0