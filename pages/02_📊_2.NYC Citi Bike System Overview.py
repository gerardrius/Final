import streamlit as st

import pandas as pd

import src.cleaning as cleaning
import src.visualizations as visual
import plotly.express as px
import codecs
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium, folium_static
from folium import Figure #, HeatMapWithTime

st.set_page_config(
    page_title = 'Visualizations on Citi Bike Service', 
    page_icon = '📊',
    layout = 'wide',
    initial_sidebar_state = 'expanded',
)

st.sidebar.markdown('')

interest = st.sidebar.selectbox('Subcategories', ['Introduction', 'Stations', 'Overall Trip Information', 'Demographics'])

# 1. Show the data
st.title("Overview of NYC Citi Bike Service")

# interest = st.selectbox('What Citi Bike feature interests you the most?', ['Stations', 'Overall Trip Information', 'Demographics'])
# st.write(f'You selected: {interest}')


df = pd.read_csv('data/april_2014.csv')


if interest == 'Stations':

    specific_interest = st.selectbox(f'What insights on {interest} would you like to visualize?', ['Activity', 'AM/PM Trip Distribution', 'Monthly Animation'])


    if specific_interest == 'AM/PM Trip Distribution':
        # day = st.select_slider('Select a day', options=('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'), label_visibility="visible")

        with st.expander("See explanation"):
            st.write('''
            The map below shows if a station have more trips started during the morning or the afternoon,
            signaled with light and dark blue respectively.
            ''')
            # st.image("https://static.streamlit.io/examples/dice.jpg")

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

        st_map = st_folium(figure4, width = 850)


    elif specific_interest == 'Activity':
        n = st.selectbox('Choose the number of rows to be displayed:', [5, 10, 20, 50])
        st.dataframe(visual.top_busy_stations(df, n))

        all_stations = sorted((visual.top_busy_stations (df, 330))['Station Name'].unique())

        your_station = st.selectbox('What is your station of interest?', all_stations)            

        st.write('Your station have the following activity stats:')

        st.dataframe(visual.your_station_data(df, your_station))




    