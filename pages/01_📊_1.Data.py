import streamlit as st
import pandas as pd
import src.streamlit_cleaning as st_cleaning

# Page configuration
st.set_page_config(page_title="Data Sources", page_icon="📊")

# 1. Show the data
st.write('''
# Project DataFrames.
Below you can dive deep into the resulting dataframes obtained after cleaning and enriching the initial files.
''')

dataframe = st.selectbox('Choose one character', ['Bike trips', 'Truck trips'])
n = st.selectbox('Choose the number of rows to be displayed', [5, 10, 20, 50])

if dataframe == 'Bike trips':
    df = pd.read_csv('data/april_2014.csv')
elif dataframe == 'Truck trips':
    df = pd.read_csv('data/truck_transfers.csv')


st.dataframe(st_cleaning.show_df_sample(df, n))


st.write('''
Source of file can be found here: https://citibikenyc.com/system-data
''')

# st.selectbox, botton trigger, input texto