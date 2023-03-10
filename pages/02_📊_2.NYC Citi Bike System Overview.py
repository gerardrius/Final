import streamlit as st

import pandas as pd

import src.cleaning as cleaning
import src.visualizations as visual
import plotly.express as px
import codecs
import streamlit.components.v1 as components

from streamlit_folium import folium_static
import folium

st.set_page_config(page_title="Visualizations on Citi Bike Service", page_icon="📊")

# 1. Show the data
st.title("Overview of NYC Citi Bike Service")

interest = st.selectbox('What Citi Bike feature interests you the most?', ['Overall Trip Information', 'Stations', 'Demographics'])
st.write(f'You selected: {interest}')


df = pd.read_csv('data/april_2014.csv')


if interest == 'Stations':

    specific_interest = st.selectbox(f'What insights on {interest} would you like to visualize?', ['Activity', 'Daily Trip Distribution', 'Another'])
    n = st.selectbox('Choose the number of rows to be displayed', [5, 10, 20, 50])

    if specific_interest == 'Activity':
        st.dataframe(visual.top_busy_stations(df, n))

    elif specific_interest == 'Daily Trip Distribution':
        day = st.select_slider('Select a day', options=('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'), label_visibility="visible")


        st.write(visual.testfunct(df, day))