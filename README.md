# Final-Project

09/03/2023:
What I have achieved:


What I want to do:
    Figure out truck pick ups
    Big files
    Streamlit app deployment

10/03/2023
What I achieved yesterday:
    Big files
    Deployed app
    Started visualizations for maps

What I want to achieve:
    Classify visualizations
        Stations
        Demographics
        Trip information

    Encapsulate into functions
        Deploy them in Streamlit

    Distance function so that it saves results every x time.

13/3
What I have
    Vis on demographics, overall info
    Not real distance


What I want to do
    Finish stations info
    Deploy everything in streamlit app
    To start tomorrow with predictor
    
14/3 What I did
    Finished stations info
    Deployed them in streamlit
    All ok

14/3 TO DO
    START FIGURING OUT:
    - Capacity of each of the goddamn station
    - Put a number of bikes / free docks to each station by 15 min differences / for each weekday.
    - Based on that, predict according to day and hour what is the availability of bikes/free docks for station

    - Create the time calculator from A TO B!
    

**Exploratory Data Analysis**

Cleaning process:

- Prepare data (cleaning and enriching)

    - Add new information (trip distance, duration, start district, end district, trip cost)

- Upload data to SQL

Query database to plot and visualize:

- Yearly trips (Time Series)
- Start and end points with Heatmap, allowing user to choose periods
- Citi Bike Stations in New York (Map Plot)
- Most used Stations
- Trip distance and duration (correlation) find routes
- Bikes Data (Electric vs. Classic, Most used bikes, etc.) make supervised learning classification model 
- Membership Analysis (Revenue Stream, Pie Chart, Subsidies, etc.)

- Try to obtain most common routes (some Google Maps resource to calculate possible routes from A to B, bike rails available) to plot heatmaps and suggest potential bike rail improvements.

**Predictive Data Analysis**

Use data to develop some models that are useful to:

- Predict trip real duration from user's initial location and desired destination (using user start and end location, and time input) 
    
    - Take into account distance to closest station, bike availability, closest station to end point, availability, etc.)


- Suggest operation routes ro relocate bikes among stations. 

- Predict short term specific station availability and general use rate for Citi system.

OSM Open Street Maps OSM nx.


Bibliography
Boeing, G. 2017. OSMnx: New Methods for Acquiring, Constructing, Analyzing, and Visualizing Complex Street Networks. Computers, Environment and Urban Systems 65, 126-139. doi:10.1016/j.compenvurbsys.2017.05.004