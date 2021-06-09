#!/usr/bin/env python3
import os
import pandas as pd
from google.cloud import storage

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


if __name__ == '__main__':
    # Testing download
    gcp = GCPHandler('twitch_data/top_streams_2450.csv')
    print(f'Fetching from {gcp.BUCKET_NAME}')
    gcp.download_from_gcp()
    print('Downloaded')
    streams = pd.read_csv('top_streams_2450.csv')
    print(streams.head())
    print(gcp.GOOGLE_APPLICATION_CREDENTIALS)