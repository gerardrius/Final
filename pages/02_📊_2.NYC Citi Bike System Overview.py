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


if interest == 'Introduction':
    st.subtitle('Welcome to NYC Citi Bike reports!')
        
    st.write('In this page, you will find all kind of data, statistics and visualizations that will help you understand the public usageof NYC Citi Bike Service. You can choose among three categories to dive deeper into.')
    # It would be nice to have some images with stations, trips and demographics and clicking them drives you to the actual subpage!


# STATIONS
elif interest == 'Stations':

    # Available plots: stations activity (with pick yours), AM/PM Map (should include button for starts or ends), Monthly/Weekday animation heatmap (cool if kepler or something).
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

# OVERALL CITI STATS
elif interest == 'Overall Trip Information':
    
    # Available plots: duration, displacement, average pace, Monthly trips, trips by weekday, in a selectbox
    st.selectbox('What you wish to see?', ['Trip duration', 'Trip distance', 'Trip average pace', 'Monthly trips', 'Trips by weekday'])

    # For this visualizations, it would be nice to be able to put color / divide somehow by gender and user type according to app user interests


# DEMOGRAPHICS
elif interest == 'Demographics':
    # Available plots: age distribution, gender distribution, user type

    # you will have to change all df names in the test notebook so that each visualization has its own unique name
    # and this file does not confuse them (specially those for birth year dist/age not defined)
    pass
    