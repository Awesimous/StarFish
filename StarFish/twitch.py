#!usr/bin/env python3

import os
import sys
from twitchAPI.twitch import Twitch
from dotenv import load_dotenv
import requests
from twitchAPI.twitch import Twitch
import pandas as pd

load_dotenv()

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
USER_TOKEN = os.environ.get('USER_TOKEN')



# Utility functions for making requests
def authorize(CLIENT_ID = CLIENT_ID, CLIENT_SECRET = CLIENT_SECRET):
    '''Get OAuth token'''
    x = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials")
    x = x.json()
    token = x["access_token"]

    return token

def request(api_endpoint, headers, params):
    '''Return a resource as json'''
    response = requests.get(
        url = api_endpoint, headers = headers, params = params).json()

    return response


# define functions to handle each endpoint
def search_channels(display_name):
    '''Get channel id, login name, and language from an exact streamer handle'''
    API_ENDPOINT = base_url + 'search/channels'
    params = {
        'query': display_name,
        'first': 1
        }

    return request(API_ENDPOINT, headers, params)['data'][0]


def get_channel_teams(channel_id):
    '''Get the list of teams to which a streamer belongs by streamer id'''
    API_ENDPOINT = base_url + 'teams/channel'
    params = {
        'broadcaster_id': channel_id
        }

    return request(API_ENDPOINT, headers, params)['data']


def get_teams(team_name, team_id):
    '''Get team membership and status data from team name and team id'''
    API_ENDPOINT = base_url + 'teams'
    params = {
        'name': team_name,
        'id': team_id
        }

    return request(API_ENDPOINT, headers, params)


def get_stream_tags(channel_id):
    API_ENDPOINT = base_url + 'streams/tags'
    params = {
        'broadcaster_id': channel_id
        }

    return request(API_ENDPOINT, headers, params)['data']


def get_top_games(first = 100):
    '''return the top n games currently viewed on the platform'''
    API_ENDPOINT = base_url + 'games/top'
    params = {
        'first': first
        }

    return request(API_ENDPOINT, headers, params)


def get_games(game_id, game_name):
    API_ENDPOINT = base_url + 'games'
    params = {
        'id': game_id,
        'name': game_name
        }

    return request(API_ENDPOINT, headers, params)


def get_all_stream_tags(first = 100, after = None, tag_id = None):
    API_ENDPOINT = base_url + 'tags/streams'
    if after:
        params = {
            'after': after,
            'first': first
            }
    elif tag_id:
        params = {
            'tag_id': tag_id
            }
    else:
        params = {
            'first': first
            }


    return request(API_ENDPOINT, headers, params)

def search_categories(query, first = 100, after = None):
    API_ENDPOINT = base_url + 'search/categories'
    params = {
        'query': query,
        'first': first
        }
    if after:
        params['after'] = after

    return request(API_ENDPOINT, headers, params)



# Functions for collection and aggregation
def get_streamer_data(display_name):
    '''Relate a streamer handle to their id, language, and login name'''
    streamer = {}

    data = search_channels(display_name)
    streamer['id'] = data['id']
    streamer['broadcaster login'] = data['broadcaster_login']
    streamer['broadcaster language'] = data['broadcaster_language']

    data = get_stream_tags(streamer['id'])
    if data:
        for tag in data:
            streamer['tag IDs'] = [tag['tag_id'] for tag in data]


    return streamer


def get_streamer_teams(display_name):
    '''Return team information for a given streamer'''
    streamer_id = search_channels(display_name)['id']
    teams = {'streamer_id': streamer_id}

    data = get_channel_teams(streamer_id)
    if data:
        for i, team in enumerate(data):
            teams[i] = {
                'team name': team['team_name'],
                'team display name': team['team_display_name'],
                'team display name': team['team_display_name'],
                'team updated at': team['updated_at'],
                'team created at': team['created_at'],
                'team info': team['info'],
                'team id': team['id']
            }


    return teams



def identify_relevant_teams(display_names):
    '''Return a dataframe of teams comprising the streamers passed'''
    pass



if __name__ == '__main__':
    # Create an instance of the twitch API client
    twitch = Twitch(CLIENT_ID, CLIENT_SECRET)
    twitch.authenticate_app([])

    # Get the ID of the user accessing the resource
    user_info = twitch.get_users(logins=['Awesimous'])
    user_id = user_info['data'][0]['id']

    # Use the token to "authenticate"
    headers = {
            'Client-ID' : CLIENT_ID,
            'Authorization': f'Bearer {USER_TOKEN}'
        }

    # Define the base url
    base_url = 'https://api.twitch.tv/helix/'

    broadcaster_name = sys.argv[1]

    channel = get_streamer_data(broadcaster_name)
    teams = get_streamer_teams(broadcaster_name)
    print(channel, '\n\n', teams)
