import streamlit as st
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import streamlit_wordcloud as wordcloud
from geopy import geocoders
from geopy.geocoders import Nominatim

# df = pd.read_csv('notebooks/streamer_df_25pages')
# st.write(df.head)

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
