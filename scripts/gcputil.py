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

def list_buckets():
    """Lists all buckets."""
    storage_client = storage.Client()
    buckets = storage_client.list_buckets()

    for bucket in buckets:
        print(bucket.name)

    return list(buckets)


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        print(blob.name)



if __name__ == '__main__':
    #print(f'Fetching from {BUCKET_NAME}')
#    GCPFileHandler('twitch_data/top_streams_2450.csv').download_from_gcp()
    #print('Downloaded')
#    streams = pd.read_csv('top_streams_2450.csv')
#    print(streams.head())
#    print(GCPFileHandler().GOOGLE_APPLICATION_CREDENTIALS)

    #GCPFileHandler('twitch_data/top_streams_2450.csv')\
    #.download_from_gcp('StarFish/data/raw/top_streams_2450.csv')
    list_blobs('starfish-databases')
