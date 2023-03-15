# Basics
import streamlit as st
import pandas as pd
import numpy as np

# For Map
import folium
from folium import Figure
from streamlit_folium import st_folium

# Others
from urllib.error import URLError

# Source files
import src.visualizations as visual

# Dataframes
april = pd.read_csv('data/april_2014.csv')

# Page configuration
st.set_page_config(
    page_title = "Your Trip", 
    page_icon = "🗺️"
)

# Tabs
tab1, tab2 = st.tabs(['🚲 Instructions', '🚀 Your Trip'])

# Introduction
tab1.title("Welcome to Your Bike Trip!")

tab1.markdown('In this section, you will be able to get a detailed route from your actual location to your destination. The application provides the closest station to the start and end points with bike and free docks availability respectively. In addition, it provides the shortest path and a total time estimation for the whole trip.')
        

start_station = tab1.selectbox('Pick your start station!', visual.get_all_stations (april))
end_station = tab1.selectbox('Pick your end station!', visual.get_all_stations (april))

def get_pos(lat,lng):
    return lat,lng

m = folium.Map(location=[40.7230679, -73.974965513],zoom_start=13)
folium.TileLayer('cartodbpositron').add_to(m)

m.add_child(folium.LatLngPopup())

map = st_folium(m, height=550, width=850)

list_of_coordinates = []
data = get_pos(map['last_clicked']['lat'],map['last_clicked']['lng'])
list_of_coordinates.append(data)
    

if data is not None:
    st.write(data)

#####

ma = folium.Map(location=[40.7230679, -73.974965513],zoom_start=13)
folium.TileLayer('cartodbpositron').add_to(m)

ma.add_child(folium.LatLngPopup())

mapa = st_folium(m, height=550, width=850)

list_of_coordinates = []
data2 = get_pos(mapa['last_clicked']['lat'],mapa['last_clicked']['lng'])
list_of_coordinates.append(data2)
    

if data2 is not None:
    st.write(data2)

#def get_pos(lat,lng):
#    return lat,lng
#list_of_coordinates = []

#figure10 = Figure(width=850,height=550)
#new_york10 = folium.Map(location=[40.7230679, -73.974965513],zoom_start=13)
#folium.TileLayer('cartodbpositron').add_to(new_york10)
#figure10.add_child(new_york10)

#data = get_pos(new_york10['last_clicked']['lat'],new_york10['last_clicked']['lng'])

#if data is not None:
#    list_of_coordinates.append(data)
#    tab1.write(data)
#    if len(list_of_coordinates) > 2:
#        tab1.write('More than 2 locations selected. Please, refresh the page and choose only two coordinates!')

# Your goddamn trip!!!