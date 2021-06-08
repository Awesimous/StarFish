from geopy import geocoders
from geopy.geocoders import Nominatim
import streamlit as st

def country_lat_long(country):
    geolocator = Nominatim(user_agent='myapplication')
    state.location = geolocator.geocode(country)
    latitude = state.location[1][0]
    longitude = state.location[1][1]
    return latitude, longitude

def city_lat_long(city):
    geolocator = Nominatim(user_agent='myapplication')
    state.location = geolocator.geocode(city)
    latitude = state.location[1][0]
    longitude = state.location[1][1]
    return latitude, longitude

@st.cache
def get_map_data(cities):
    coords = []
    for city in cities:
        city_data = city_lat_long(city)
        coords.append([city_data[0], city_data[1]])
    return pd.DataFrame(
        np.array(coords),
        columns=['lat', 'lon'])