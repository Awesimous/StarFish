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
from StarFish.data import GCPFileHandler
from StarFish.twitter import twitter_viewer_locations, get_streamer_data, get_streamer_data_filtered
import altair as alt
from StarFish.images import load_image, image_tag, background_image_style
from StarFish.plots import lineplot, get_10_recent_streams, time_processing
import base64
from StarFish.maps import country_lat_long, city_lat_long, get_map_data


# Download dbs on initial setup
print('Going to gcp')
GCPFileHandler('scraped_data/streamers_clean.csv')\
    .download_from_gcp('StarFish/data/streamers_clean.csv')
print('Downloaded')
stream_df = pd.read_csv('StarFish/data/streamers_clean.csv')
print('Showing')
st.table(stream_df.head())
print('Shown')

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
    state.games_df = pd.read_csv('StarFish/data/games_clean.csv')
    state.df = pd.read_csv('StarFish/data/streamers_clean.csv')
    # create a range of 200 users
    state.target_df = state.df[500:700]
    state.usernames = state.target_df.username.to_list()
    #set usernames as index
    state.target_df = state.df[500:700].set_index('username')
    # drop outliers as they make range setting difficult
    state.target_df = state.target_df.drop('ESL_CSGO')
    #make a list with all users in the range

    state.max_followers = int(state.target_df["Total Followers"].max())
    state.max_viewer = int(state.target_df['AVG Viewers'].max())
    st.write('Select games you think could be interesting for your product:')
    c1, c2 = st.beta_columns((1, 1))
    with c1:
        game_1 = st.checkbox('WoW')
        game_2 = st.checkbox('Grand Theft Auto V')
        game_3 = st.checkbox('VALORANT')
        game_4 = st.checkbox('Call of Duty: Warzone')
        game_5 = st.checkbox('Minecraft')
    with c2:
        option_c = st.checkbox('Fortnite')
        option_b = st.checkbox('League of Legends')
        option_l = st.checkbox('Just Chatting')
        option_i = st.checkbox('All Other Games Combined')

    state.games_temp = ['Just Chatting', 'Grand Theft Auto V',
                'League of Legends',
                'VALORANT',
                'Minecraft',
                'Call of Duty: Warzone',
                'World of Warcraft',
                'Fortnite',
                'Counter-Strike: Global Offensive',
                'All Other Games Combined']
    state.social_media = ['Twitter', 'YouTube']
    st.write("---")
    state.target_games = st.multiselect('Select games you are interested in:', state.games_temp)
    state.viewer = st.slider('Minimum Average Viewer per Hour', 1, state.max_viewer, 1000)
    state.target_df = state.target_df[state.target_df['AVG Viewers'] >= state.viewer]
    state.follower = st.slider('Minimum Total Follower', 1, state.max_followers, 5000)
    state.target_df = state.target_df[state.target_df['Total Followers'] >= state.follower]
    state.features = st.multiselect('Select feature:', state.target_df.columns)
    state.feature_df = state.target_df[state.features]
    if state.features:
        state.col_sort = st.radio('Select feature to sort on:', state.feature_df.columns)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        st.write(f'You selected {state.col_sort}!')
    state.social = st.multiselect('Select social media:', state.social_media)



def display_state_values(state):
    st.write('Display the 5 best streamers (or less) based on your chosen categories:')
    # show dataframe with 5 best streamers based on selection criterias
    state.feature_df = state.feature_df.sort_values(by=[state.col_sort], ascending=False).head()
    st.dataframe(state.feature_df)
    # select one target to specify data on
    state.target = st.radio('Do you want to look at any streamer in particular?', state.feature_df.index)
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

    # with c1:
    #     expander=st.beta_expander("expand")
    #     with expander:
    #         state.games_df = pd.read_csv('StarFish/data/games_clean.csv')
    #         state.top_games_max_viewers = state.games_df.sort_values(by = ['Avg. viewers'], ascending=False)
    #         state.top_10 = state.top_games_max_viewers.head(10)

    #         fig = make_subplots(rows=1, cols=2)
    #         #fig = px.pie(state.top_10)
    #         fig.add_trace(go.pie(state.top_10, values='Max. viewers', names='Game', 
    #                             title='Max Viewers Top 10 Games', 
    #                             color_discrete_sequence=px.colors.sequential.RdBu),
    #                     row=1,col=1)

    #         fig.update_layout(height=300, width=800, title_text="Side By Side Subplots")

    #         g = st.plotly_chart(fig)
        #c4, c5, c6 = st.beta_columns((1, 1, 2))
    
    # prepare data for plotting (import and process)
    # index streams for one specific user
    state.stream_df = pd.read_csv('StarFish/data/top_streams_2450.csv')
    
    # selecting df for target
    state.target_stream = state.stream_df[state.stream_df['User'] == state.target]
    state.target_df = state.feature_df.loc[state.target]
    
    # updating processing to allow for plots:
    state.target_stream = time_processing(state.target_stream)
    
    # import games_df
    state.games_df = pd.read_csv('notebooks/CSVs/Games_df')
    
    state.target_games_df = state.games_df[state.games_df['User'] == state.target]
    st.dataframe(state.target_games_df)
    state.top_games_max_viewers = state.target_games_df.sort_values(by = ['Avg. viewers'], ascending=False)
    state.top_games_followers_gained = state.target_games_df.sort_values(by =['Followers per hour'], ascending=False)
    state.top_10_followers_gained = state.top_games_followers_gained.head(10)
    state.top_10 = state.top_games_max_viewers.head(10)
    state.recent_streams = get_10_recent_streams(state.stream_df, state.target)
    st.table(state.recent_streams)
    #plot the data
    
    fig = make_subplots(rows=1, 
                        cols=2,
                        subplot_titles=("Pie 1", "Pie 2"), 
                        specs=[
                        [{"type": "domain"}, {"type": "domain"}]
                        ])
    fig.add_trace(go.Pie(labels=state.top_10_followers_gained["Game"], values=state.top_10_followers_gained['Followers per hour']), 1, 1)
    fig.add_trace(go.Pie(labels=state.top_games_followers_gained["Game"].head(10), values=state.top_games_followers_gained['Followers per hour']), 1, 2)
    fig.update_layout(
        showlegend=True,
        uniformtext_minsize=12, 
        uniformtext_mode='hide')

    st.plotly_chart(fig)

    fig = make_subplots(rows=1, 
                        cols=2,
                        subplot_titles=("Pie 1", "Pie 2"), 
                        specs=[
                        [{"type": "domain"}, {"type": "domain"}]
                        ])
    fig.add_trace(go.Pie(labels=state.recent_streams['Duration'], values=state.recent_streams['AVG Viewers']), 1, 1)
    fig.add_trace(go.Pie(labels=state.recent_streams['AVG Viewers'], values=state.recent_streams['daytime_classifier']), 1, 2)
    fig.update_layout(
        showlegend=True,
        uniformtext_minsize=12, 
        uniformtext_mode='hide')

    st.plotly_chart(fig)

## trying to implement lineplots


    # state.new_range = state.target_stream.iloc[::20, :][['AVG Viewers', 'MAX Viewers']]
    # st.table(state.new_range)
    
    st.title('Some other Stuff with plots')
    fig_line = px.line(lineplot(state.target_stream, 'month', 'AVG Viewers'))
    st.plotly_chart(fig_line)

    # st.plotly_chart(fig)

    # fig = make_subplots(rows=1, 
    #                     cols=2,
    #                     subplot_titles=("Pie 1", "Pie 2"), 
    #                     specs=[
    #                     [{"type": "domain"}, {"type": "domain"}]
    #                     ])
    # add a bridge to get twitter name for specific target (StarFish/socials_clean.csv)
    
    state.socials = pd.read_csv('StarFish/data/socials_clean.csv')
    state.social_target = state.socials[state.socials['username'] == state.target]
    # for Twitter
    state.twitter = state.social_target['Twitter']

    c3, c4 = st.beta_columns((1, 1))

    with c3:
        st.title('Twitter')
        image_path = 'images/Twitter.png'
        image_link = f'https://twitter.com/{state.twitter.iloc[0]}'
        st.write('Click here to get redirected to the Streamer Twitter Page!')
        st.write(f'<a href="{image_link}">{image_tag(image_path)}</a>', unsafe_allow_html=True)
        if st.checkbox('Show background image', False):
            st.write(background_image_style(image_path), unsafe_allow_html=True)
        try:
            state.twitter_df = get_streamer_data_filtered(state.twitter)
            st.dataframe(state.twitter_df[['text', 'retweet_count', 'created_at']])
        except:
            st.info('No Data found on Twitter for that Twitch User')
 
    state.youtube = state.social_target['YouTube']
    st.write(state.youtube)
    with c4:
        st.title('YouTube')
        image_path = 'images/YouTube.png'
        image_link = f'https://toutube.com/{state.toutube.iloc[0]}'
        st.write('Click here to get redirected to the Streamer YouTube Page!')
        st.write(f'<a href="{image_link}">{image_tag(image_path)}</a>', unsafe_allow_html=True)
        if st.checkbox('Show background image', False):
            st.write(background_image_style(image_path), unsafe_allow_html=True)
        st.write('More info to follow')
        # try:
        #     state.twitter_df = get_streamer_data_filtered(state.twitter)
        #     st.dataframe(state.twitter_df[['text', 'retweet_count', 'created_at']])
        # except:
        #     st.info('No Data found on Twitter for that Twitch User')
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
    state.test = ['London', 'Bristol', 'New Brunswick']
    
    df = get_map_data(state.test)
    st.map(df)
    # temp_table = get_streamer_data_filtered('shroud')
    # st.table(temp_table) 
         
    # fig = make_subplots(rows=2, 
    #                     cols=2,
    #                     subplot_titles=("Pie 1", "Pie 2", "Pie 3", 'Pie 4'), 
    #                     specs=[
    #                     [{"type": "domain"}, {"type": "domain"}],
    #                     [{"type": "domain"}, {"type": "domain"}]
    #                     ])
    # fig.add_trace(go.Pie(labels=state.top_10_followers_gained["Game"], values=state.top_10_followers_gained['Followers per hour']), 1, 1)
    # fig.add_trace(go.Pie(labels=state.top_games_followers_gained["Game"], values=state.top_games_followers_gained['Followers per hour']), 1, 2)
    # #fig.add_trace(go.Pie(labels=state.top_10_followers_gained["Game"], values=state.top_10_followers_gained['Followers per hour']), 2, 1)
    # #fig.add_trace(go.Pie(labels=state.top_10_followers_gained["Game"], values=state.top_10_followers_gained['Followers per hour']), 2, 2)
    # fig.update_layout(
    #     showlegend=True,
    #     uniformtext_minsize=12, 
    #     uniformtext_mode='hide')

    # st.plotly_chart(fig)



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
