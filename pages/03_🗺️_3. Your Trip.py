# Basics
import streamlit as st
import pandas as pd
import numpy as np

# For Map
import folium
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

m = folium.Map()

m.add_child(folium.LatLngPopup())

map = st_folium(m, height=350, width=700)


data = get_pos(map['last_clicked']['lat'],map['last_clicked']['lng'])

if data is not None:
    st.write(data)


# Your goddamn trip!!!