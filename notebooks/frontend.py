import streamlit as st
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from geopy import geocoders
from geopy.geocoders import Nominatim
from requests.api import get
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from StarFish.twitch import search_channels
import requests
from bs4 import BeautifulSoup


def parse_games_2(user_name):
    user_name.lower()
    headers = {'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'}
    response = requests.get(url = f"https://twitchtracker.com/{user_name}/games", headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    df=pd.read_html(str(soup))[0]
    return df

st.title('Twitch dashboard')
st.markdown('The dashboard will visualize statistics of each streamer')
st.sidebar.title('Visualization Selector')

df = pd.read_csv('streamer_df_clean')
username = df['username']


display = (df['username'])

df_games = parse_games_2('Bruncky')
st.table(df_games)

 

options = list(range(len(display)))

value = st.sidebar.selectbox("username", options, format_func=lambda x: display[x])

st.sidebar.write(df.loc[value]['AVG Viewers'])
#st.sidebar.text_input('name:',value)
#st.sidebar.text_input('sth:')

print(value)

#st.bar_chart(pd.DataFrame([value]))
#st.line_chart()
#df2=parse_games_2('Shroud')

#st.table(df2)
#st.line_chart(value)
fig = plt.figure(figsize=(12,8))
x = range(1,len(df_games['Followers'])+1)
plt.plot(x, df_games['Followers'])
#st.line_chart(df_games['Followers'])
st.pyplot(fig)


def city_lat_long(city):
    geolocator = Nominatim(user_agent='myapplication')
    location = geolocator.geocode(city)
    latitude = location[1][0]
    longitude = location[1][1]
    return latitude, longitude
def country_lat_long(country):
    geolocator = Nominatim(user_agent='myapplication')
    location = geolocator.geocode(country)
    latitude = location[1][0]
    longitude = location[1][1]
    return latitude, longitude
test = ['London', 'Bristol', 'New Brunswick']
@st.cache
def get_map_data(cities):
    coords = []
    for city in cities:
        city_data = city_lat_long(city)
        coords.append([city_data[0], city_data[1]])
    return pd.DataFrame(
            np.array(coords),
            columns=['lat', 'lon']
        )
df = get_map_data(test)
st.map(df)