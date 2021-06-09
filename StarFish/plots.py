import pandas as pd
import streamlit as st

def time_assignment(x):
    '''Support function to classify streams by time when they are on air'''
    if x == 1.0:
        return 'morning'
    elif x == 2.0:
        return 'afternoon'
    elif x == 3.0:
        return 'evening'
    else:
        return 'night'

def time_processing(df):
    '''Input a dataframe for streams of individual streamers for datetime processing'''
    df['new_date'] = pd.to_datetime(df['new_date'])
    df = df[df.new_date > '2015-01-01']
    df['month'] = df['new_date'].dt.to_period('M')
    df['month'] =  df['month'].astype(str)
    df.daytime_classifier = df.daytime_classifier.apply(lambda x: time_assignment(x))
    return df

def lineplot(df, x, y):
    return pd.crosstab(df[x], df[y])

def get_10_recent_streams(df, streamer):
    '''gets the 10 most recent streams of each user
       input: name of the streamer in ''
       csv:top_2450.csv
    '''
    streamer_df = df[df['User']== streamer]
    streamer_df['last_seen'] = streamer_df['new_date'] +' '+streamer_df['new_time']
    streamer_df['last_seen'] = pd.to_datetime(streamer_df['last_seen'])
    streamer_df = streamer_df.sort_values(by=['last_seen'], ascending=False)
    ten_recent_streams = streamer_df.head(10)
    return ten_recent_streams
