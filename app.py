import streamlit as st
import time
import datetime as dt
from datetime import datetime
import numpy as np
import plotly.express as px
import requests
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import wordcloud
from geopy import geocoders
from geopy.geocoders import Nominatim
from plotly.subplots import make_subplots
from streamlit.hashing import _CodeHasher
from StarFish.twitch import search_channels
from bs4 import BeautifulSoup
from StarFish.twitter import twitter_viewer_locations, get_streamer_data_filtered, get_streamer_data
from StarFish.data import GCPFileHandler
from PIL import Image
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from StarFish.data import GCPFileHandler, clean_gamer_df
from StarFish.twitter import twitter_viewer_locations, get_streamer_data, get_streamer_data_filtered
import altair as alt
from StarFish.images import load_image, image_tag, background_image_style
from StarFish.plots import lineplot, get_10_recent_streams, time_processing
import base64
from StarFish.maps import country_lat_long, city_lat_long, get_map_data
from StarFish.games_info import games_dict


#Download dbs on initial setup
# print("GCP DOWNLOAD")
# GCPFileHandler('twitch_data/top_streams_2450.csv')\
#     .download_from_gcp('StarFish/data/top_streams_2450.csv')
# print("GCP DOWNLOAD")
# stream_df = pd.read_csv('StarFish/data/top_streams_2450.csv')
# print("DOWNLOAD COMPLETE")
# st.table(stream_df.head())

st.set_page_config(layout="wide", page_icon=":art:", page_title="StarFish")

def main():
    # import all relevant csv files
    state = _get_state()
    pages = {
        "Input": page_settings,
        "Dashboard": page_dashboard,
    }

    st.sidebar.title(":floppy_disk: Navigation bar")
    page = st.sidebar.radio("Select your page", tuple(pages.keys()))

    # Display the selected page with the session state
    pages[page](state)

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


def page_dashboard(state):
    st.title(":chart_with_upwards_trend: Dashboard page")
    st.markdown('The dashboard will visualize statistics of each streamer')
    display_state_values(state)


def page_settings(state):
    st.title(":wrench: Set your input")
    #display_state_values(state)
    state.games_df = pd.read_csv('StarFish/data/games_sample.csv')
    ## we might want to implement some plots with data from bigger streamer as for our sample there is a problem to retrieve the data (more info with Simon)
    #state.stream_df = pd.read_csv('StarFish/data/top_2450.csv')

    state.df = pd.read_csv('StarFish/data/sample_df.csv')
    state.df = state.df.rename(columns={'Minimum followers gained on average per hour om air' : 'Minimum followers gained on average per hour on air'})
    state.usernames = state.df.Username.to_list()
    state.df_user = state.df.set_index('Username')
    st.table(state.df.head())
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
    state.games_info = pd.DataFrame.from_dict(games_dict, orient='index', columns=['Category', 'Created by', 'Release Date', 'Recommended Age', 'Likes pct'])
    st.write("---")
    #st.table(state.target_df)
    #state.feature_df = state.target_df[state.features]
    # st.write('Select games you think could be interesting for your product:')
    # state.games_selection = st.multiselect('Select games you are interested in:', list(state.games_info.index.values))
    # state.target_df["10 most played games"]= state.target_df["10 most played games"].str.join('')
    # state.target_df = state.target_df[state.target_df['10 most played games'].isin(state.games_selection)]
    # st.table(state.target_df)
    state.features = st.multiselect('Select which features you are interested in', state.df_user[["AVG Viewers", 'Time Streamed (in hours)','Hours Watched','Followers Gained', 'Total Followers','Total Views','All Time Peak Viewers']].columns)
    state.features = state.df_user[state.features]
    state.features.dropna(inplace=True)
    state.features = state.features.clip(lower=0)
    if "AVG Viewers" in state.features:
        state.avg_viewer = st.slider('Minimum Average Viewer per Hour', 1, int(state.features['AVG Viewers'].max()), 1000)
        state.features = state.features[state.features['AVG Viewers'] >= state.avg_viewer]
    if "Time Streamed (in hours)" in state.features:
        state.time_streamed = st.slider('Minimum time streamed in total hours', 1, int(state.features['Time Streamed (in hours)'].max()), 1000)
        state.features = state.features[state.features['Time Streamed (in hours)'] >= state.time_streamed]
    if 'Hours Watched' in state.features:
        state.hours_watched = st.slider('Minimum hours watched', 1, int(state.features['Hours Watched'].max()), 1000)
        state.features = state.features[state.features['Hours Watched'] >= state.hours_watched]
    if 'Followers Gained' in state.features:
        state.followers_hour = st.slider('Minimum followers gained on average per hour on air', 1, int(state.features['Followers Gained'].max()), 1000)
        state.features = state.features[state.features['Followers Gained'] >= state.followers_hour]
    if "Total Followers" in state.features:
        state.total_follower = st.slider('Minimum Total Follower', 1, int(state.features['Total Followers'].max()), 1000)
        state.features = state.features[state.features['Total Followers'] >= state.total_follower]
    if "Total Views" in state.features:
        state.total_views = st.slider('Minimum Total Views', 1, int(state.features['Total Views'].max()), 1000)
        state.features = state.features[state.features['Total Views'] >= state.total_views]
    if "All Time Peak Viewers" in state.features:
        state.peak = st.slider('Minimum All Time Peak Viewers', 1, int(state.features['All Time Peak Viewers'].max()), 1000)
        state.features = state.features[state.features['All Time Peak Viewers'] >= state.peak]

    
    st.write("Select any of the following social media channels to include:")
    c3, c4, c5 = st.beta_columns((1, 1, 1))
    with c3:
        state.twitter = st.checkbox('Twitter')
        if state.twitter:
            twitter_img ="images/Twitter.png"
            twitter_open = Image.open(twitter_img)
            st.image(twitter_open, width=100)
    with c4:
        state.youtube = st.checkbox('YouTube')
        if state.youtube:
            youtube_img ="images/YouTube.png"
            youtube_open = Image.open(youtube_img)
            st.image(youtube_open, width=150)
    with c5:
        state.instagram = st.checkbox('Instagram')
        if state.instagram:
            instagram_img ="images/Instagram.png"
            instagram_open = Image.open(instagram_img)
            st.image(instagram_open, width=100)


def display_state_values(state):
    st.write('Display the 5 best streamers (or less) based on average viewer:')
    # show dataframe with 5 best streamers based on selection criterias
    state.top_5 = state.features.head()
    st.table(state.top_5)
    state.col_sort = st.radio('Please select one feature to use for ranking the streamers:', state.features.columns)
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    st.write(f'You selected {state.col_sort}, good choice!')
    # state.temp_time = ["morning", "afternoon", "evening", "night"]
    # state.time = st.radio('Which time you want your star to be streaming at?', state.temp_time)
    # st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    state.features = state.features.sort_values(by=[state.col_sort], ascending=False).head()
    # select one target to specify data on
    state.target = st.radio('Do you want to look at any streamer in particular?', state.top_5.index)
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    state.target_df = state.features.loc[state.target]
    #st.bar_chart(state.targets_df)
    st.title('Top 10 Games for your main target')
    state.games_target = state.games_df[state.games_df['Username'] == state.target]
    state.top_games_target = state.games_target.sort_values(by=['AVG Viewers']).head()
    state.top_games_sample = state.games_df.sort_values(by=['AVG Viewers']).head()
    
    fig = go.Pie(labels=state.top_games_target["Game"], values= state.top_games_target["AVG Viewers"])

    st.write(fig)
    
    # fig, ax1 = plt.subplots(figsize=(10, 5))
    # plt.figure(figsize=(10, 5))
    
    # def label_function(val):
    #     return f'{val:.0f}%'

    # fig, ax1 = plt.subplots(figsize=(10, 5))
    # plt.figure(figsize=(10, 5))
    # state.data_df = pd.DataFrame(state.top_games[["Game", "AVG Viewers"]])
    # state.data_df.size().plot(
    #     kind='pie',
    #     colors=['tomato', 'lightgrey', '#b5eb9a'],
    #     autopct=label_function,
    #     ax=ax1)
    # st.write(fig)


    # st.title("Overview of 5 most recent live sessions on Twitch")
    # st.table(state.recent_streams.head())
    #plot the data
    
    # fig = make_subplots(rows=1, 
    #                     cols=2,
    #                     subplot_titles=("Pie 1", "Pie 2"), 
    #                     specs=[
    #                     [{"type": "domain"}, {"type": "domain"}]
    #                     ])
    # fig.add_trace(go.Pie(labels=state.target_games_df["Game"]), 1, 1)
    # fig.add_trace(go.Pie(labels=state.target_games_df["Game"]), 1, 2)
    # fig.update_layout(
    #     showlegend=True,
    #     uniformtext_minsize=12, 
    #     uniformtext_mode='hide')


    # for Twitter
    state.twitter_name = state.df[state.df['Username'] == state.target]['Twitter']
    c6, c7 = st.beta_columns((1, 1))

    with c6:
        if state.twitter_name.iloc[0]:
            st.title('Twitter')
            image_path = 'images/Twitter.png'
            image_link = f'https://twitter.com/{state.twitter_name.iloc[0]}'
            st.write('Click here to get redirected to the Streamer Twitter Page!')
            st.write(f'<a href="{image_link}">{image_tag(image_path)}</a>', unsafe_allow_html=True)
            if st.checkbox('Show background image', False):
                st.write(background_image_style(image_path), unsafe_allow_html=True)
            
            state.twitter_df = get_streamer_data_filtered(state.twitter_name.iloc[0])
            st.dataframe(state.twitter_df[['text', 'retweet_count', 'created_at']])
        else:  
            st.info('No Data found on Twitter for that Twitch User')
 
    with c7:
        if state.df_user.loc[state.target, ['YouTube']]:
            st.title('YouTube')
            image_path = 'images/YouTube.png'
            image_link = f'https://toutube.com/{state.youtube.loc[state.target]}'
            st.write('Click here to get redirected to the Streamer YouTube Page!')
            st.write(f'<a href="{image_link}">{image_tag(image_path)}</a>', unsafe_allow_html=True)
            if st.checkbox('Show background image', False):
                st.write(background_image_style(image_path), unsafe_allow_html=True)
            st.table(df_user.loc[state.target,[['YT Viewcount', 'YT Subscribers', 'YT Videocount']]])


    # expander=st.beta_expander("expand")
    # with expander:
    #     fig = make_subplots(rows=1, 
    #                         cols=2,
    #                         subplot_titles=("Pie 1", "Pie 2"), 
    #                         specs=[
    #                         [{"type": "domain"}, {"type": "domain"}]
    #                         ])
    #     fig.add_trace(go.Pie(labels=state.top_10_followers_gained["Game"], values=state.top_10_followers_gained['Followers per hour']), 1, 1)
    #     fig.add_trace(go.Pie(labels=state.top_games_followers_gained["Game"], values=state.top_games_followers_gained['Followers per hour']), 1, 2)
    #     fig.update_layout(
    #         showlegend=True,
    #         uniformtext_minsize=12, 
    #         uniformtext_mode='hide')

    #     st.plotly_chart(fig)
    
    st.write(state.df)
    state.locations = state.df.loc[state.target,['Twitter Community Locations']]
    state.cities = state.locations['cities']
    state.print = get_map_data(state.cities)
    st.map(state.print)



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
    #         state.clear()


class _SessionState:

    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


if __name__ == "__main__":
    main()
