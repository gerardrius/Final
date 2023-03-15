# Basics
import pandas as pd
import numpy as np

# Functions
import src.visualizations as visual

# Streamlit
import streamlit as st
import streamlit.components.v1 as components
import codecs
from PIL import Image

# Graph Visualizations
import seaborn as sns
import matplotlib.pyplot as plt
import folium
import plotly.express as px

# For maps
import folium
import folium.plugins
from folium import Figure
from folium.plugins import HeatMapWithTime
from streamlit_folium import st_folium, folium_static

# Visualizations page configuraiton
st.set_page_config(
    page_title = 'Visualizations on Citi Bike Service', 
    page_icon = '📊',
    layout = 'wide',
    initial_sidebar_state = 'expanded',
)

df = pd.read_csv('data/april_2014.csv')

tab1, tab2, tab3, tab4 = st.tabs(['🔍 Introduction' ,'🚲 Stations', '📊 Overall Trip Information', '👥 Demographics'])

# 1. Introduction
tab1.title("Overview of NYC Citi Bike Service")

tab1.header('Welcome to NYC Citi Bike reports!')

tab1.markdown('In this page, you will find all kind of data, statistics and visualizations that will help you understand the public usage of NYC Citi Bike Service. You can choose among three categories to dive deeper into **Overall Trip Information**, **Stations** and **Demographics**.')

introduction_image = Image.open('pages/images/introduction.jpg')

tab1.image(introduction_image, caption = 'Citi Station in NYC')


# 2. Stations

tab2.title("Stations' Activity and Stats")

tab2.header('Get the most information about Citi Stations!')

your_station = tab2.selectbox('Pick your favorite station!', visual.get_all_stations (df))
if your_station:
    tab2.dataframe(visual.your_station_data (df, your_station))

starts_classification = tab2.checkbox('Stations with the most trips started')
if starts_classification:
    n1 = tab2.select_slider('Select how many results to be shown', options = range(1, 101))
    tab2.dataframe(visual.top_n_starts(df, n1))

ends_classification = tab2.checkbox('Stations with the most trips ended')
if ends_classification:
    n2 = tab2.select_slider('Select how many results to be shown', options = range(1, 101))
    tab2.dataframe(visual.top_n_ends(df, n2))

most_busy_stations = tab2.checkbox('Most busy stations overall')
if most_busy_stations:
    n3 = tab2.select_slider('Select how many results to be shown', options = range(1, 101))
    tab2.dataframe(visual.top_busy_stations(df, n3))

starts_map = tab2.checkbox('Starts Distribution (AM/PM)')
if starts_map:
    tab2.markdown(':blue[Light blue]: most starts in the **morning**.')

    tab2.markdown(':blue[Light blue]: most starts in the **evening**.')
    with tab2:
        st_folium(visual.starts_distribution(df), width = 850)

ends_map = tab2.checkbox('Ends Distribution (AM/PM)')
if ends_map:
    tab2.markdown(':blue[Light blue]: most ends in the **morning**.')

    tab2.markdown(':blue[Dark blue]: most ends in the **afternoon**.')

    with tab2:
        st_folium(visual.ends_distribution(df), width = 850)

# plot_heatmap = tab2.checkbox('Hourly activivity this month')
# if plot_heatmap:
#     day = tab4.select_slider('Select a weekday', options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
#     tab2.st_map = st_folium(visual.heatmapWithTime(df, day), width = 850)


# 3. Overall trip Information
tab3.title('Overall Trip Information')

tab3.subheader('Choose the trip stats  below that interest you the most!')
duration = tab3.checkbox('Trip Duration')
if duration:
    tab3.plotly_chart(visual.duration_distribution(df))

displacement = tab3.checkbox('Trip Displacement')
if displacement:
    tab3.plotly_chart(visual.displacement_distribution(df))

pace = tab3.checkbox('Trip Speed')
if pace:
    tab3.plotly_chart(visual.average_pace_distribution(df))

month = tab3.checkbox('Month Trips')
if month:
    tab3.plotly_chart(visual.monthly_trips(df))

day = tab3.checkbox('Weekday Trips')
if day:
    tab3.plotly_chart(visual.trips_by_day(df))

hour = tab3.checkbox('Hourly Trips')
if hour:
    tab3.plotly_chart(visual.trips_by_hour(df))


# 4. Demographics
tab4.title('Demographics Information')

tab4.subheader('Choose the demographic information below that interest you the most!')

age_dist = tab4.checkbox('Age Distribution')
if age_dist:
    tab4.plotly_chart(visual.age_distribution(df))
    col3, col4 = tab4.columns(2)
    col3.metric('Number of users without age defined', f'{visual.age_not_defined (df)[0]}')
    col4.metric('Percentage over total users', f'{round(visual.age_not_defined (df)[1], 3)*100}')

gender_dist = tab4.checkbox('Gender Distribution')
if gender_dist:

    day = tab4.select_slider('Select a weekday', options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    tab4.write(f'Use by gender on {day}s.')
    tab4.plotly_chart(visual.gender_distribution(df, day))

    col1, col2 = tab4.columns(2)
    col1.metric('Number of users without gender defined', f'{visual.gender_not_defined (df)[0]}')
    col2.metric('Percentage over total users', f'{round(visual.gender_not_defined (df)[1], 3)*100}')

user_type = tab4.checkbox('User Type Distribution')
if user_type:
    day = tab4.select_slider('Select a weekday', options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    tab4.write(f'Use by member or custimer on {day}s.')
    tab4.plotly_chart(visual.user_type (df, day))
