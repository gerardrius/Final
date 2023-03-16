# LIBRARIES
import pandas as pd
import numpy as np

# Trip duration
import datetime
from datetime import datetime, timedelta

# Trip distance
import geopy.distance
import osmnx as ox
from osmnx import graph_from_bbox
import networkx as nx
import taxicab as tc
from shapely.geometry import Point, LineString

    # FUNCTIONS FOR OLD CSV FORMAT (E.G. 2014)
# COLUMN STANDARIZATION
def rename_columns (df):
    df.rename(columns={
        'tripduration': 'duration','starttime': 'started_at', 'stoptime': 'ended_at', 'start station id': 'start_station_id',
        'start station name': 'start_station_name', 'start station latitude': 'start_lat', 
        'start station longitude': 'start_lng', 'end station id': 'end_station_id', 'end station name': 'end_station_name', 
        'end station latitude': 'end_lat', 'end station longitude': 'end_lng', 'bikeid': 'bike_id', 'usertype': 'member_casual', 
        'birth year': 'birth_year', 'gender': 'gender'}, inplace = True)
    return df

    # FUNCTIONS TO CLEAN ANY CSV FORMAT
# STRAIGHT LINE DISTANCE
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

# HOUR ONLY (24H FORMAT)
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

# DATE WITHOUT TIME
def get_date (df):
    df['trip_date'] = pd.to_datetime(df['started_at'].apply(lambda x: x[:10]))
    return df

# TURN START AND END TIMES INTO DATETIME FORMAT
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

# GET NOMINAL DAY AND MONTH
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

# DAY OF THE WEEK IS WEEKDAY OR WEEKEND 
def is_weekend (df):
    df['weekend'] = df['weekday'].apply(lambda x: 1 if x in ['Saturday', 'Sunday'] else 0)
    return df

# REAL TRIP DISTANCE WITH SHORTEST AVAILABLE ROUTE
def get_graph_from_bbox (df):
    max_start_lat, max_end_lat = df.start_lat.max(), df.end_lat.max()
    max_start_lng, max_end_lng = df.start_lng.max(), df.end_lng.max()

    min_start_lat, min_end_lat = df.start_lat.min(), df.end_lat.min()
    min_start_lng, min_end_lng = df.start_lng.min(), df.end_lng.min()

    ymax = max(max_start_lat, max_end_lat)
    xmax = max(max_start_lng, max_end_lng)
    ymin = min(min_start_lat, min_end_lat)
    xmin = min(min_start_lng, min_end_lng)
    G = graph_from_bbox(ymax, ymin, xmin, xmax, network_type='drive', simplify=True)

    return G

def get_real_distance (df, G):
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

# NON BIKE TRIPS STATION BALANCE
def single_station_balance (df, station_name, day):
    unique_days = df.trip_date.unique()
    balance_mensual_estacion = []
    for day in unique_days:
        llegadas = df[(df['end_station_name'] == station_name) & (df['trip_date'] == day)].shape[0]
        salidas = df[(df['start_station_name'] == station_name) & (df['trip_date'] == day)].shape[0]
        balance_mensual_estacion.append(llegadas - salidas)
    
    return balance_mensual_estacion

# CHECK IF A BIKE HAS NOT BEEN TRANSPORTED
def bike_not_transported (df, bike_id, date):  # fix date setting
    '''
    If bike is not transported return true
    '''
    bike_trips = df[(df['bike_id'] == bike_id) & df['trip_date'] == date]
    start_list = []
    end_list = []
    for i, row in bike_trips.iterrows():  
        start_list.append(row['start_station_name'])
        end_list.append(row['end_station_name'])

    start_list = start_list[1:]
    end_list = end_list[:-1]

    if start_list == end_list:
        return True
    else:
        return False

# BIKE ROUTE
def bike_route (df, bike_id):
    bike_trips = df[df['bike_id'] == bike_id]
    bike_journey = []
    start_station = []
    end_station = []

    for index, row in bike_trips.iterrows():
        start_station.append(row['start_station_name'])
        end_station.append(row['end_station_name'])

    start_station = start_station[1:]
    end_station = end_station[:-1]

    for i in range(len(start_station)):
        next_start, last_end = start_station[i], end_station[i]
        bike_journey.append((next_start, last_end))
        
    return bike_journey

# ALL BIKES' ROUTES
def all_bikes_journey (df):
    bikes_journey_list = []
    for bike_id in df['bike_id'].unique():
        bikes_journey_list.append(bike_route (df, bike_id))
    
    return bikes_journey_list

# DICTIONARY WITH NON BIKE TRIPS INFO
def non_trip_mobility_dict (df):
    list_of_start_stations = df.start_station_name.unique().tolist()
    list_of_end_stations = df.end_station_name.unique().tolist()
    all_stations = list(set(list_of_start_stations + list_of_end_stations))
    mobility_dictionary = {}

    for station_name in all_stations:
        if station_name in list_of_start_stations:
            mobility_dictionary[station_name] = {
                'id': df[df['start_station_name'] == station_name].iloc[0]['start_station_id'], 
                'receives_from': [],
                'sends_to': [],             
            }
        elif station_name in list_of_end_stations:
            mobility_dictionary[station_name] = {
                'id': df[df['end_station_name'] == station_name].iloc[0]['end_station_id'], 
                'receives_from': [],
                'sends_to': []                
            }           

    return mobility_dictionary

# FROM WHERE RECEIVES AND WHERE SENDS:
def transportations (dictionary, bikes_journey_list):
    for bike_journey in bikes_journey_list:
        for arrival_departure in bike_journey:
            if arrival_departure[0] != arrival_departure[1]:
                dictionary[arrival_departure[1]]['sends_to'].append(arrival_departure[0])
                dictionary[arrival_departure[0]]['receives_from'].append(arrival_departure[1])

    return dictionary

# STATION BALANCE
def station_balance (dictionary):
    for key, value in dictionary.items():
        value['bikes_received'] = len(value['receives_from'])
        value['bikes_sent'] = len(value['sends_to'])
        value['balance'] = (value['bikes_received'] - value['bikes_sent']) 
        # if receives more than sends (balance > 0): station is likely to be a start point
        # else if sends more than receives (balance < 0): station is likely to be an end point
    
    return dictionary

# SINGLE ID TRUCK TRANSFERS
def single_bike_truck_transfers (df, bike_id):
    bike_trips = df[df['bike_id'] == bike_id]
    last_end_station_name = []
    last_end_station_id = []
    last_end_time = []
    next_start_station_name = []
    next_start_station_id = []
    next_start_time = []


    for i, row in bike_trips.iterrows():
        last_end_station_id.append(row['end_station_id'])
        last_end_station_name.append(row['end_station_name'])
        last_end_time.append(row['ended_at'])
        next_start_station_id.append(row['start_station_id'])
        next_start_station_name.append(row['start_station_name'])
        next_start_time.append(row['started_at'])

    last_end_station_id = last_end_station_id[:-1]
    last_end_station_name = last_end_station_name[:-1]
    last_end_time = last_end_time[:-1]

    next_start_station_id = next_start_station_id[1:]
    next_start_station_name = next_start_station_name[1:]
    next_start_time = next_start_time[1:]

    # Definitive lists
    end_id = []
    end_name = []
    end_time = []
    start_id = []
    start_name =[]
    start_time = []
    bike_id_list = []

    for i in range(len(last_end_station_name)):
        if last_end_station_id[i] != next_start_station_id[i]:
            end_id.append(last_end_station_id[i])
            end_name.append(last_end_station_name[i])
            end_time.append(last_end_time[i])
            start_id.append(next_start_station_id[i])
            start_name.append(next_start_station_name[i])
            start_time.append(next_start_time[i])
            bike_id_list.append(bike_id)
    
    transfers_df = pd.DataFrame({
        'last_end_station_id': end_id, 
        'last_end_station_name': end_name,
        'last_end_time': end_time,
        'next_start_station_id': start_id,
        'next_start_station_name': start_name,
        'next_start_time': start_time,
        'bike_id': bike_id_list
    })

    return transfers_df

# ALL TRANSFERS
def all_transfers (df):
    dataframes_list = []
    for bike_id in df['bike_id'].unique():
        dataframes_list.append(single_bike_truck_transfers (df, bike_id))
    
    all_transfers_df = pd.concat(dataframes_list, ignore_index = True)
    all_transfers_df.sort_values(by = ['last_end_time'], ascending = True, inplace = True)
    all_transfers_df.reset_index(drop = True, inplace = True)
    return all_transfers_df

def datetime_format_trucks (df):
    last_end_time = []
    next_start_time = []
    for i, row in df.iterrows():
        last = datetime.strptime(row['last_end_time'], '%Y-%m-%d %H:%M:%S')
        next = datetime.strptime(row['next_start_time'], '%Y-%m-%d %H:%M:%S')

        try:
            last_end_time.append(last)
            next_start_time.append(next)
        except:
            last_end_time.append(np.nan)
            next_start_time.append(np.nan)

    df['last_end_time'] = last_end_time
    df['next_start_time'] = next_start_time
    return df

    # CLEAN NEW FORMAT
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


    # FOR COLAB
# Split dataframe into n subdataframes to be uploaded to drive and run distance function to them.
def dataframe_split (df, n):
    april_split = np.array_split(df, n)
    for i in range(len(april_split)):
        april_split[i].to_csv(f'data/splitted_csv/split_{i}.csv')

# Upload csv's to Colab

# And run this loop after passing the two functions required to get G and Real Distance
'''
for i in range(len(split_list)):
  converting = get_real_distance (split_list[i])
  converting.to_csv(f'split_{i}.csv', index = False)
  files.download(f'split_{i}.csv')
'''


# FOR TRUCKS AND PREDICTIVE PART:

def stations_coordinates (origin_df):
    # Subdataframes with all stations with trip starts (both 329)
    starts = origin_df[['start_station_id', 'start_station_name', 'start_lat', 'start_lng']].groupby(by=['start_station_name']).mean().reset_index()
    ends = origin_df[['end_station_id', 'end_station_name', 'end_lat', 'end_lng']].groupby(by=['end_station_name']).mean().reset_index()

    # Homogeneization of both dataframes
    starts.rename(columns={'start_station_name': 'station_name', 'start_station_id': 'station_id', 'start_lat': 'lat', 'start_lng': 'lng'}, inplace = True)
    ends.rename(columns={'end_station_name': 'station_name', 'end_station_id': 'station_id', 'end_lat': 'lat', 'end_lng': 'lng'}, inplace = True)

    # Concatenation and removing duplicated stations (330 unique instances)
    stations = pd.concat([starts, ends], join = 'outer', ignore_index = True)
    stations = stations.drop_duplicates('station_name', ignore_index=True)

    return stations

def geo_points_stations (df):
    coordinate_list = []
    for i, row in df.iterrows():
        coordinate_list.append((row['lat'], row['lng']))
    df['coordinates'] = coordinate_list
    return df

def coordinate_columns (df):
    last_station_lat = ['last_lat']*df.shape[0]
    last_station_lng = ['last_lng']*df.shape[0]
    next_station_lat = ['next_lat']*df.shape[0]
    next_station_lng = ['next_lng']*df.shape[0]

    df.insert(3, 'last_end_lat', last_station_lat)
    df.insert(4, 'last_end_lng', last_station_lng)

    df['next_start_lat'] = next_station_lat
    df['next_start_lng'] = next_station_lng

    return df

def truck_trips_coordinates (coordinates_origin, truck_df):
    last_lat = []
    last_lng = []
    next_lat = []
    next_lng = []

    for i, row in truck_df.iterrows():
        last_lat.append(coordinates_origin[coordinates_origin['station_name'] == row['last_end_station_name']]['lat'].iloc[0])
        last_lng.append(coordinates_origin[coordinates_origin['station_name'] == row['last_end_station_name']]['lng'].iloc[0])
        next_lat.append(coordinates_origin[coordinates_origin['station_name'] == row['next_start_station_name']]['lat'].iloc[0])
        next_lng.append(coordinates_origin[coordinates_origin['station_name'] == row['next_start_station_name']]['lng'].iloc[0])

    truck_df['last_end_lat'] = last_lat
    truck_df['last_end_lng'] = last_lng
    truck_df['next_start_lat'] = next_lat
    truck_df['next_start_lng'] = next_lng

    return truck_df

def time_difference (df):
    df['started_at'] = pd.to_datetime(df['started_at'], infer_datetime_format = True)
    df['ended_at'] = pd.to_datetime(df['ended_at'], infer_datetime_format = True)
    return df

def bike_human_truck_trips (df, bike_id):
    last_end = df[df['bike_id'] == bike_id]['end_station_id'].to_list()[:-1]
    etime = df[df['bike_id'] == bike_id]['ended_at'].to_list()[:-1]

    next_start = df[df['bike_id'] == bike_id]['start_station_id'].to_list()[1:]
    stime = df[df['bike_id'] == bike_id]['started_at'].to_list()[1:]

    result_df = pd.DataFrame({'last_end': last_end, 'ended_at': etime, 'next_start': next_start, 'started_at': stime})
    
    result_df = time_difference(result_df)

    result_df['time_difference'] = result_df['started_at'] - result_df['ended_at']

    for i, row in result_df.iterrows():
        if row['last_end'] != row['next_start']:
            last_end.append(row['next_start'])
            next_start.append(row['last_end'])
            stime.append(row['ended_at'] + 0.2 * row['time_difference'])
            etime.append(row['started_at'] - 0.2 * row['time_difference'])

    result_df = pd.DataFrame({'last_end': last_end, 'ended_at': etime, 'next_start': next_start, 'started_at': stime})

    result_df = time_difference(result_df)

    last_trip_ends = result_df[['last_end', 'ended_at']].sort_values(by=['ended_at'], ascending=True).reset_index()
    next_trip_starts = result_df[['next_start', 'started_at']].sort_values(by=['started_at'], ascending=True).reset_index()

    final_df = pd.concat([last_trip_ends, next_trip_starts], axis=1, ignore_index=True)
    final_df.rename(columns = {1: 'last_end', 2: 'ended_at', 4: 'next_start', 5: 'started_at'}, inplace = True)
    final_df.drop([0, 3], axis = 1, inplace = True)

    final_df = time_difference(final_df)

    final_df['time_difference'] = final_df['started_at'] - final_df['ended_at']
    final_df['bike_id'] = [bike_id]*final_df.shape[0]

    return final_df

def concat_all_bike_trips (df):
    df_list = []
    for bike_id in df.bike_id.unique().tolist():
        df_ = bike_human_truck_trips(df, bike_id)
        df_list.append(df_)

    ALL_TRIPS = pd.concat(df_list, ignore_index = True)
    
    return ALL_TRIPS


# Capacity calculator
def capacity_dictionary (df):
    difference_dict = {}
    bench_date = '2014-05-01'
    datetime_obj_bench = datetime.strptime(bench_date, '%Y-%m-%d')

    df = time_difference(df)
    ends = df[df['ended_at'] <= datetime_obj_bench].last_end.value_counts().to_frame().reset_index().rename(columns = {'index': 'id', 'last_end': 'counts'})
    starts = df[df['started_at'] <= datetime_obj_bench].next_start.value_counts().to_frame().reset_index().rename(columns = {'index': 'id', 'next_start': 'counts'})

    total = ends.merge(starts, how='outer', on='id')
    total['difference'] = total['counts_x'] - total['counts_y']

    for i, row in total.iterrows():
        difference_dict[row['id']] = []

    time_range = [dt.strftime('%Y-%m-%d') for dt in 
       datetime_range(datetime(2014, 4, 1, 0), datetime(2014, 5, 1, 0, 5), 
       timedelta(days=1))]

    for date in time_range:
        date_time_obj = datetime.strptime(date, '%Y-%m-%d')

        ends = df[df['ended_at'] <= date_time_obj].last_end.value_counts().to_frame().reset_index().rename(columns = {'index': 'id', 'last_end': 'counts'})
        starts = df[df['started_at'] <= date_time_obj].next_start.value_counts().to_frame().reset_index().rename(columns = {'index': 'id', 'next_start': 'counts'})

        total = ends.merge(starts, how='outer', on='id')
        total['difference'] = total['counts_x'] - total['counts_y']

        for i, row in total.iterrows():
            difference_dict[row['id']].append(row['difference'])

    for key, value in difference_dict.items():
        difference_dict[key] = rounder(max(value))

    return difference_dict

def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta

def rounder (num):
    if num <= 20:
        return 20
    else:
        if round(num, -1) >= num:
            return round(num, -1)
        else:
            return round(num, -1) + 10 