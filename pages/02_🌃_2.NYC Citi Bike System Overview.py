import streamlit as st
import src.cleaning as cleaning

# 1. Show the data
st.write("Adventure time data: cleaned")
st.dataframe(cleaning.load_dataframe())