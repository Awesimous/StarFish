import streamlit as st
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from geopy import geocoders
from geopy.geocoders import Nominatim
import wordcloud

from StarFish.twitch import search_channels
import requests
from bs4 import BeautifulSoup
from StarFish.twitter import twitter_viewer_locations, get_streamer_data_filtered, get_streamer_data
import time

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

df = pd.read_csv('StarFish/data/channels.csv')
#username = df['username']


#display = (df['username'])

#df_games = parse_games_2('Bruncky')
#st.table(df_games)

#options = list(range(len(display)))

games_temp = ['Just Chatting', 'Grand Theft Auto V',
              'League of Legends',
              'VALORANT',
              'Minecraft',
              'Call of Duty: Warzone',
              'World of Warcraft',
              'Fortnite',
              'Counter-Strike: Global Offensive',
              'All Other Games Combined']

#value = st.sidebar.selectbox("username", options, format_func=lambda x: display[x])
games = st.sidebar.multiselect('Select game:', games_temp)
viewer = st.sidebar.slider('Minimum Average Viewer per Hour', 1, 200000, 1000)
df = df[df['AVG Viewers'] >= viewer]
follower = st.sidebar.slider('Minimum Total Follower', 1, 10000000, 5000)
df = df[df['Total Followers'] >= follower]

st.table(df)
# st.sidebar.write(df.loc[value]['AVG Viewers'])
#st.sidebar.text_input('name:',value)
#st.sidebar.text_input('sth:')

selected_indices = st.multiselect('Select streamer by index:', df.index)
target = df.iloc[0]
if selected_indices:
    st.write(target)

#df_games = parse_games_2('Bruncky')
#st.table(df_games)
#print(value)

#st.bar_chart(pd.DataFrame([value]))
#st.line_chart()
#df2=parse_games_2('Shroud')

#st.table(df2)
#st.line_chart(value)
# fig = plt.figure(figsize=(12,8))
# x = range(1,len(df_games['Followers'])+1)
# plt.plot(x, df_games['Followers'])
# #st.line_chart(df_games['Followers'])
# st.pyplot(fig)


locations = twitter_viewer_locations(consumer_key, consumer_secret, access_token,access_token_secret, 'shroud', '2018-01-01', 100)


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
df = get_map_data(locations['cities'])
st.map(df)

temp_table = get_streamer_data_filtered('shroud')
st.table(temp_table)

words = [
    dict(text="Robinhood", value=16000, color="#b5de2b", country="US", industry="Cryptocurrency"),
    dict(text="Personio", value=8500, color="#b5de2b", country="DE", industry="Human Resources"),
    dict(text="Boohoo", value=6700, color="#b5de2b", country="UK", industry="Beauty"),
    dict(text="Deliveroo", value=13400, color="#b5de2b", country="UK", industry="Delivery"),
    dict(text="SumUp", value=8300, color="#b5de2b", country="UK", industry="Credit Cards"),
    dict(text="CureVac", value=12400, color="#b5de2b", country="DE", industry="BioPharma"),
    dict(text="Deezer", value=10300, color="#b5de2b", country="FR", industry="Music Streaming"),
    dict(text="Eurazeo", value=31, color="#b5de2b", country="FR", industry="Asset Management"),
    dict(text="Drift", value=6000, color="#b5de2b", country="US", industry="Marketing Automation"),
    dict(text="Twitch", value=4500, color="#b5de2b", country="US", industry="Social Media"),
    dict(text="Plaid", value=5600, color="#b5de2b", country="US", industry="FinTech"),
]
return_obj = wordcloud.visualize(words, tooltip_data_fields={
    'text':'Company', 'value':'Mentions', 'country':'Country of Origin', 'industry':'Industry'
}, per_word_coloring=False)

st.button("Re-run")

pts = 50
x1 = np.arange(pts)
y1 = np.random.random(pts)
y2 = np.random.random(pts)
y3 = (x1/pts)**2

fig = make_subplots(rows=1, cols=2)

fig.add_trace(go.Scatter(x=x1,y=y1,
                    mode='markers',
                    name='markers'),row=1,col=1)
fig.add_trace(go.Scatter(x=x1,y=y2,
                    mode='markers',
                    name='markers2'),row=1,col=2)
fig.add_trace(go.Scatter(x=x1,y=y3,
                    mode='lines',
                    name='lines'),row=1,col=2)

fig.update_layout(height=300, width=800, title_text="Side By Side Subplots")

g = st.plotly_chart(fig)
