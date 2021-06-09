#!/usr/bin/env python3
import os
import sys
import time
import pandas as pd
import StarFish.twitch as tw
from google.cloud import storage
from twitchAPI.twitch import Twitch

def clean_gamer_df(df):
    df.reset_index(inplace=True)
    df['Total airtime'] = df['Total airtime'].astype(str).str[:-1]
    df[['Followers per hour', 'to_remove']] = df['Followers'].str.split(' /',expand=True)
    df = df.drop(columns = ['Followers', 'to_remove'])
    df['Total airtime'] = df['Total airtime'].str.split(' ',expand=True)
    df['Followers per hour'] = df['Followers per hour'].apply(lambda x: float(x))
    df['Last seen'] = pd.to_datetime(df['Last seen'])
    df = df.rename(columns = {'#':'id'})
    df['id'] = df['id'].astype(str).str[1]
    df = df.set_index('id')

    return df

class GCPFileHandler:
    '''Upload and download arbitrary files from the databases bucket'''
    BUCKET_NAME = 'starfish-databases'
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    def __init__(self, storage_location):
        # 'twitch_data/top_streams_2450.csv'
        self.STORAGE_LOCATION = storage_location

    def upload_to_gcp(self, file):
        client = storage.Client()
        bucket = client.bucket(self.BUCKET_NAME)
        blob = bucket.blob(self.STORAGE_LOCATION)
        blob.upload_from_filename(file)

    def download_from_gcp(self, file):
        client = storage.Client()
        bucket = client.bucket(self.BUCKET_NAME)
        blob = bucket.blob(self.STORAGE_LOCATION)
        blob.download_to_filename(file)

class TwitchFilesHandler:
    ''''''
    def __init__(self):
        self.USER_TOKEN = tw.authorize()

        self.twitch = Twitch(tw.CLIENT_ID, tw.CLIENT_SECRET)
        self.twitch.authenticate_app([])

        # Get the ID of the user accessing the resource
        user_info = self.twitch.get_users(logins=['Awesimous'])
        #user_id = user_info['data'][0]['id']

        # Use the token to "authenticate"
        self.headers = {
                'Client-ID' : tw.CLIENT_ID,
                'Authorization': f'Bearer {self.USER_TOKEN}'
            }

        self.base_url = 'https://api.twitch.tv/helix/'

    def get_tags(self):
        streamer_names = pd.read_csv('StarFish/data/streamers_clean.csv')['username']
        streamer_names = streamer_names.head()
        channels = pd.DataFrame()
        for username in streamer_names:
            streamer = tw.get_streamer_data(self.headers, username)
            for val in streamer.values(): list(val)
            print(streamer)
            print('\n')
            channel = pd.DataFrame(streamer)
            channel['username'] = username
            print(channel)
            print('\n')
            print('\n')
            channels = pd.concat([channels, channel])
            time.sleep(1)
            """streams['id'] = channel['id']
            streams['username'] = username
            streams['login_name'] = channel['broadcaster_login']
            streams['channel_tags'] = channel['tag_ids']"""
        return channels


    def clean_gamer_df(df):
        df['Total airtime'] = df['Total airtime'].astype(str).str[:-1]
        df[['Followers per hour', 'to_remove']] = df['Followers'].str.split(' /',expand=True)
        df = df.drop(columns = ['Followers', 'to_remove'])
        df[['Total airtime','Percentage of total airtime']] = df['Total airtime'].str.split(' ',expand=True)
        df['Percentage of total airtime'] = df['Percentage of total airtime'].apply(lambda x: float(x))
        df['Followers per hour'] = df['Followers per hour'].apply(lambda x: float(x))
        df['Last seen'] = pd.to_datetime(df['Last seen'])
        df = df.rename(columns = {'#':'id'})
        df['id'] = df['id'].astype(str).str[1]
        df = df.set_index('id')

        return df



if __name__ == '__main__':
    if sys.argv[1] == 'gcp':
        # Testing download
        gcp = GCPFileHandler('twitch_data/top_streams_2450.csv')
        print(f'Fetching from {gcp.BUCKET_NAME}')
        gcp.download_from_gcp()
        print('Downloaded')
        streams = pd.read_csv('top_streams_2450.csv')
        print(streams.head())
        print(gcp.GOOGLE_APPLICATION_CREDENTIALS)

    if sys.argv[1] == 'twitch':
        base_url = 'https://api.twitch.tv/helix/'
        print(TwitchFilesHandler().get_tags())