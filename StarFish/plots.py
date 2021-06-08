import pandas as pd
import streamlit as st

def lineplot(df, column):
    df['new_date'] = pd.to_datetime(df['new_date'])
    df['month'] = df['new_date'].dt.to_period('M')
    df_grouped = df.groupby('month', as_index = False)[[column]].sum()
    df_grouped['month'] =  df_grouped['month'].astype(str)
    chart_data = pd.DataFrame(
        df_grouped[column])
    return st.line_chart(chart_data)

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


