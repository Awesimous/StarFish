#!/usr/bin/env python3
import os
import pandas as pd
from google.cloud import storage


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