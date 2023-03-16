import streamlit as st
import pandas as pd
import src.streamlit_cleaning as st_cleaning

# Page configuration
st.set_page_config(page_title="Data Sources", page_icon="📂")

# 1. Show the data
st.header('Project DataFrames')

st.markdown('Below you can dive deeper into the some of the resulting dataframes obtained after cleaning and enriching the initial files. Bike trips dataframe is mainly the transformed initial _csv_ file after some cleaning, whereas truck and all trips represent some of the resulting dataframes obtained after tracking _non-human_ trips.')

dataframe = st.selectbox('Choose one topic', ['Bike trips', 'Truck trips', 'All trips'])
n = st.selectbox('Choose the number of rows to be displayed', [5, 10, 20, 50])

if dataframe == 'Bike trips':
    df = pd.read_csv('data/april_2014.csv')
elif dataframe == 'Truck trips':
    df = pd.read_csv('data/truck_transfers.csv')
elif dataframe == 'All trips':
    df = pd.read_csv('data/all_trips.csv')


st.dataframe(st_cleaning.show_df_sample(df, n))