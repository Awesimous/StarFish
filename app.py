import streamlit as st
import time
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


# Download dbs on initial setup
GCPFileHandler('twitch_data/top_streams_2450.csv')\
    .download_from_gcp('StarFish/data/raw/top_streams_2450.csv')


st.set_page_config(layout="wide",initial_sidebar_state="expanded")


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
    state.target_df = state.df[500:700].set_index('username')
    state.target_df = state.target_df.drop('ESL_CSGO')
    state.max_followers = int(state.target_df["Total Followers"].max())
    state.max_viewer = int(state.target_df['AVG Viewers'].max())
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
    state.viewer = st.slider('Minimum Average Viewer per Hour', 1, state.max_viewer, 1000)
    state.target_df = state.target_df[state.target_df['AVG Viewers'] >= state.viewer]
    state.follower = st.slider('Minimum Total Follower', 1, state.max_followers, 5000)
    state.target_df = state.target_df[state.target_df['Total Followers'] >= state.follower]
    state.features = st.multiselect('Select feature:', state.target_df.columns)
    state.feature_df = state.target_df[state.features]
    state.col_sort = st.multiselect('Select feature to sort on:', state.feature_df.columns)
    state.social = st.multiselect('Select social media:', state.social_media)



def display_state_values(state):
    st.write('Display the 5 best streamers (if there are 5) based on your chosen categories:')
    state.feature_df = state.feature_df.sort_values(by=[state.col_sort[0]], ascending=False).head()

    st.table(state.feature_df)

    # c1, c2, c3 = st.beta_columns((1, 1, 2))

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



    if st.button("Clear state"):
        state.clear()


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
