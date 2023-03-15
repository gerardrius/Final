import streamlit as st
import pandas as pd
import pydeck as pdk
from urllib.error import URLError

st.set_page_config(
    page_title = "Your Trip", 
    page_icon = "🗺️"
)

tab1 = st.tabs(['🚲 Your Bike Trip'])

tab1.title("Welcome to Your Bike Trip!")

tab1.markdown('In this section, you will be able to get a detailed route from your actual location to your destination. The application provides the closest station to the start and end points with bike and free docks availability respectively. In addition, it provides the shortest path and a total time estimation for the whole trip.')
        

