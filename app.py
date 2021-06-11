import base64
import time
import wordcloud
import requests
import streamlit as st
import datetime as dt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import altair as alt
from PIL import Image
from bs4 import BeautifulSoup
from geopy import geocoders
from datetime import datetime
from pathlib import Path
from geopy.geocoders import Nominatim
from plotly.subplots import make_subplots
from streamlit.hashing import _CodeHasher
from StarFish.twitch import search_channels
from StarFish.twitter import twitter_viewer_locations, get_streamer_data_filtered, get_streamer_data
from StarFish.data import GCPFileHandler
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from StarFish.data import GCPFileHandler, clean_gamer_df
from StarFish.twitter import twitter_viewer_locations, get_streamer_data, get_streamer_data_filtered
from StarFish.images import load_image, image_tag, background_image_style
from StarFish.plots import lineplot, get_10_recent_streams, time_processing
from StarFish.maps import country_lat_long, city_lat_long, get_map_data
import ast
from datetime import datetime

st.set_page_config(layout="wide", page_icon=":art:", page_title="StarFish")

print('Loading app.py')
print('Checking for dbs..')

p = Path('StarFish/data/streamers_clean.csv')
if p.exists():
    print('Skipping streamers_clean')
else:
    GCPFileHandler('scraped_data/streamers_clean.csv')\
        .download_from_gcp('StarFish/data/streamers_clean.csv')
    print('Downloaded streamers')

p = Path('StarFish/data/socials_clean.csv')
if p.exists():
    print('Skipping socials_clean')
else:
    GCPFileHandler('scraped_data/socials_clean.csv')\
        .download_from_gcp('StarFish/data/socials_clean.csv')
    print('Downloaded soc')

p = Path('StarFish/data/games_clean.csv')
if p.exists():
    print('Skipping games_clean')
else:
    GCPFileHandler('scraped_data/games_clean.csv')\
        .download_from_gcp('StarFish/data/games_clean.csv')
    print('Downloaded games')

p = Path('StarFish/data/top_streams_2450.csv')
if p.exists():
    print('Skipping top_streams_2450')
else:
    GCPFileHandler('scraped_data/top_streams_2450.csv')\
        .download_from_gcp('StarFish/data/top_streams_2450.csv')
    print('Downloaded top s')

p = Path('StarFish/data/sample_df.csv')
if p.exists():
    print('Skipping sample_df')
else:
    GCPFileHandler('scraped_data/sample_df.csv')\
        .download_from_gcp('StarFish/data/sample_df.csv')
    print('Downloaded combi sample')

p = Path('StarFish/data/games_sample.csv')
if p.exists():
    print('Skipping games_sample')
else:
    GCPFileHandler('scraped_data/games_sample.csv')\
        .download_from_gcp('StarFish/data/games_sample.csv')
    print('Downloaded games sample')

p = Path('StarFish/data/line_plot_data.csv')
if p.exists():
    print('Skipping streamers_clean')
else:
    GCPFileHandler('scraped_data/line_plot_data.csv')\
        .download_from_gcp('StarFish/data/line_plot_data.csv')
    print('Downloaded plots')



games_df = pd.read_csv('StarFish/data/games_sample.csv')
## we might want to implement some plots with data from bigger streamer as for our sample there is a problem to retrieve the data (more info with Simon)
#stream_df = pd.read_csv('StarFish/data/top_2450.csv')
line_plot_data = pd.read_csv('StarFish/data/line_plot_data.csv')
df = pd.read_csv('StarFish/data/sample_df.csv')
df['Time Streamed (in hours)'] = df['Time Streamed (in hours)'].apply(lambda x: int(x))
df = df.rename(columns={'Minimum followers gained on average per hour om air' : 'Minimum followers gained on average per hour on air'})
usernames = df.Username.to_list()
df_user = df.set_index('Username')
#st.table(df.head())
#set usernames as index
# drop outliers as they make range setting difficult
#make a list with all users in the range
games_dict = {
'WoW': ['MORE (Multiplayer online role-playing game)', 'Leslie Benzies, Simon Lashley, David Jones, Imran Sarwar, Billy Thomson', 2004 , 14 , '84%'],
'Grand Theft Auto V': ['Action-Adventure Game', 'David Jones and Mike Dailly', 2013, 13, '95%'],
'VALORANT': ['Tactical Shooter','Riot Games',2020, 16, '90%'],
'Call of Duty': ['First-person Shooter', 'Activision, Treyarch, Infinity Ward, Raven Software, MORE', 2003, 18, '95%'],
'Minecaft': ['Sandbox-Survival', ' Mojang', 2011, 10, ''],
'Fortnite':['Survival', 'Epic games', 2017,12,'85%'],
'League of Legends': ['MOBA (Multiplayer online battle arena)', 'Steve Feak, Mark Yetter, Tom Cadwell, Christina Norman, David Capurro, Rob Garrett', 2009, 11, '76%'],
}
games_info = pd.DataFrame.from_dict(games_dict, orient='index', columns=['Category', 'Created by', 'Release Date', 'Recommended Age', 'Likes pct'])

st.title(":chart_with_upwards_trend: Dashboard page")
st.markdown('The dashboard will visualize statistics of each streamer')


st.sidebar.title(":wrench: Set your input")
#display_state_values(state)

st.write("---")
#st.table(target_df)
#feature_df = target_df[features]
# st.write('Select games you think could be interesting for your product:')
# games_selection = st.multiselect('Select games you are interested in:', list(games_info.index.values))
# target_df["10 most played games"]= target_df["10 most played games"].str.join('')
# target_df = target_df[target_df['10 most played games'].isin(games_selection)]
# st.table(target_df)
features = st.sidebar.multiselect('Select which features you are interested in', df_user[["AVG Viewers", 'Time Streamed (in hours)','Hours Watched','Followers Gained', 'Total Followers','All Time Peak Viewers']].columns)
features = df_user[features]
features = features.clip(lower=0)
if "AVG Viewers" in features:
    avg_viewer = st.sidebar.slider('Minimum Average Viewer per Hour', 1, int(np.array(features['AVG Viewers']).max()), 1)
    features = features[features['AVG Viewers'] >= avg_viewer]
if "Time Streamed (in hours)" in features:
    time_streamed = st.sidebar.slider('Minimum time streamed in total hours', 1, int(np.array(features['Time Streamed (in hours)']).max()), 1)
    features = features[features['Time Streamed (in hours)'] >= time_streamed]
if 'Hours Watched' in features:
    hours_watched = st.sidebar.slider('Minimum hours watched', 1, int(np.array(features['Hours Watched']).max()), 1)
    features = features[features['Hours Watched'] >= hours_watched]
if 'Followers Gained' in features:
    followers_hour = st.sidebar.slider('Minimum followers gained on average per hour on air', 1, int(np.array(features['Followers Gained']).max()), 1)
    features = features[features['Followers Gained'] >= followers_hour]
if "Total Followers" in features:
    total_follower = st.sidebar.slider('Minimum Total Follower', 1, int(np.array(features['Total Followers']).max()), 1)
    features = features[features['Total Followers'] >= total_follower]
# if "Total Views" in features:
#     total_views = st.sidebar.slider('Minimum Total Views', 1, int(np.array(features['Total Views']).max()), 1)
#     features = features[features['Total Views'] >= total_views]
if "All Time Peak Viewers" in features:
    peak = st.sidebar.slider('Minimum All Time Peak Viewers', 1, int(np.array(features['All Time Peak Viewers']).max()), 1)
    features = features[features['All Time Peak Viewers'] >= peak]

st.sidebar.write("Select any of the following social media channels to include:")

twitter = st.sidebar.checkbox('Twitter')
youtube = st.sidebar.checkbox('YouTube')
instagram = st.sidebar.checkbox('Instagram')

# show dataframe with 5 best streamers based on selection criterias

if not features.empty:
    st.subheader('Display the 5 best streamers (or less):')
    top_5 = features.head()
    st.table(top_5)
    st.subheader('Please select one feature to use for ranking the streamers:')
    col_sort = st.radio('', features.columns)
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    st.write(f'You selected {col_sort}, good choice!')
    top_5 = features.sort_values(by=[col_sort], ascending=False).head()
    # temp_time = ["morning", "afternoon", "evening", "night"]
    # time = st.radio('Which time you want your star to be streaming at?', temp_time)
    # st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    st.subheader('Now let us have a look how that looks like for our selected Stars:')
    if top_5.shape[0]>1:
        fig = px.bar(top_5, x=top_5.index, y=top_5[col_sort], 
                    color=top_5.index, barmode="group")
        fig.update_layout(
            showlegend=True,
            uniformtext_minsize=12, 
            uniformtext_mode='hide')
        st.plotly_chart(fig)
    st.write('Cool Stuff, right?')
    st.markdown('----')
    # select one target to specify data on
    st.subheader('Do you want to look at any streamer in particular?')
    target = st.radio('', top_5.index)
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    target_df = df_user.loc[target]
    #st.bar_chart(targets_df)
    st.title('Top 5 Games for your main target')
    games_target = games_df[games_df['Username'] == target]
    top_games_target = games_target.sort_values(by=['AVG Viewers']).head()
    top_games_sample = games_df.sort_values(by=['AVG Viewers']).head()
    # fig = go.Pie(labels=top_games_target["Game"], values= top_games_target["AVG Viewers"])

    # st.write(fig)

    # fig = make_subplots(rows=1, 
    #                     cols=2,
    #                     subplot_titles=("Pie 1", "Pie 2"), 
    #                     specs=[
    #                     [{"type": "domain"}, {"type": "domain"}]
    #                     ])
    # fig.add_trace(go.Pie(labels=target_games_df["Game"]), 1, 1)
    # fig.add_trace(go.Pie(labels=target_games_df["Game"]), 1, 2)
    # fig.update_layout(
    #     showlegend=True,
    #     uniformtext_minsize=12, 
    #     uniformtext_mode='hide')

    # fig, ax1 = plt.subplots(figsize=(10, 5))
    # plt.figure(figsize=(10, 5))

    # def label_function(val):
    #     return f'{val:.0f}%'

      # Equal aspect ratio ensures that pie is drawn as a circle.

    # fig, ax1 = plt.subplots(figsize=(10, 5))
    # plt.figure(figsize=(10, 5))
    # plt.pie(, autopct='%1.1f%%',
    #         shadow=True, startangle=90)
    # ax1.legend(title="Games")
    # st.write(fig)

    
    fig = px.pie(
    names=top_games_target['Game'], values=top_games_target['AVG Viewers']
    )
    fig.update_layout(
        showlegend=True,
        uniformtext_minsize=12, 
        uniformtext_mode='hide')
    st.plotly_chart(fig)
    
    #select users for plot, to show difference between best, 500th, 1000th, 1500th streamer
    # st.line_chart(line_plot_data)
    # st.title("Overview of 5 most recent live sessions on Twitch")
    # st.table(recent_streams.head())
    # plot the data
    st.write('')
    st.write('----')
    if twitter:
        twitter_name = df[df['Username'] == target]['Twitter']
        c6, c7 = st.beta_columns((1, 1))

        if twitter_name.iloc[0]:
            st.title('Twitter')
            image_path = 'images/Twitter.png'
            image_link = f'https://twitter.com/{twitter_name.iloc[0]}'
            st.write('Click here to get redirected to the Streamer Twitter Page!')
            st.write(f'<a href="{image_link}">{image_tag(image_path)}</a>', unsafe_allow_html=True)
            
            twitter_df = get_streamer_data_filtered(twitter_name.iloc[0])
            twitter_user = twitter_df.set_index('Username')
            st.subheader(f'Interesting Twitter Stats for {target}')
            st.table(twitter_user[['Name','Location', 'Followers_count', 'Friends_count']].iloc[0])
            twitter_tweets = twitter_df.set_index('Created_at')
            st.subheader(f'Here are the most recent Tweets for {target}')
            st.table(twitter_tweets[['Text', 'Retweet_count']])
        else:  
            st.info('No Data found on Twitter for that Twitch User')
    st.write('')
    st.write('----')
    if youtube:
        yt_id = df_user.loc[target, ['YouTube']][0]
        yt_df = df_user[df_user['YouTube'] == yt_id][['YT Viewcount', 'YT Subscribers', 'YT Videocount']]
        if yt_id != 'nan':
            st.title('YouTube')
            image_path = 'images/YouTube.png'
            image_link = f'https://youtube.com/{yt_id}'
            st.write('Click here to get redirected to the Streamer YouTube Page!')
            st.write(f'<a href="{image_link}">{image_tag(image_path)}</a>', unsafe_allow_html=True)
            st.subheader(f'Interesting YouTube Stats for {target}')
            st.table(yt_df)
    st.write('')
    st.write('----')
    if instagram:
        st.subheader('Oh Snap!')
        image1 ="images/Instagram.png"
        original = Image.open(image1)
        st.image(original, width=100)
        st.info('Instagram Feature to come soon!')
        
    st.write('')
    st.write('----')
    if twitter:
        locations = df_user.loc[target]['Twitter Community Locations']
        locations = ast.literal_eval(locations)
        cities = locations.get('cities', None)
        countries = locations.get('countries', None)
        if cities:
            st.subheader(f'Let\'s have a look at where {target}\'s community is')
            print = pd.concat([get_map_data(cities),get_map_data(countries)], axis=0, ignore_index=True)
            st.map(print, zoom=2)
        else: 
            st.info('No data found on the communication location')



    # words = [
    #     dict(text="Robinhood", value=16000, color="#b5de2b", country="US", industry="Cryptocurrency"),
    #     dict(text="Personio", value=8500, color="#b5de2b", country="DE", industry="Human Resources"),
    #     dict(text="Boohoo", value=6700, color="#b5de2b", country="UK", industry="Beauty"),
    #     dict(text="Deliveroo", value=13400, color="#b5de2b", country="UK", industry="Delivery"),
    #     dict(text="SumUp", value=8300, color="#b5de2b", country="UK", industry="Credit Cards"),
    #     dict(text="CureVac", value=12400, color="#b5de2b", country="DE", industry="BioPharma"),
    #     dict(text="Deezer", value=10300, color="#b5de2b", country="FR", industry="Music Streaming"),
    #     dict(text="Eurazeo", value=31, color="#b5de2b", country="FR", industry="Asset Management"),
    #     dict(text="Drift", value=6000, color="#b5de2b", country="US", industry="Marketing Automation"),
    #     dict(text="Twitch", value=4500, color="#b5de2b", country="US", industry="Social Media"),
    #     dict(text="Plaid", value=5600, color="#b5de2b", country="US", industry="FinTech"),
    # ]
    # return_obj = wordcloud.visualize(words, tooltip_data_fields={
    #     'text':'Company', 'value':'Mentions', 'country':'Country of Origin', 'industry':'Industry'
    # }, per_word_coloring=False)
    # if st.button("Clear state"):
    #         clear()
