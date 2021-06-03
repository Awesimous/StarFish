#!usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys
from pathlib import Path


def parse_html(url):
    '''Read a webpage and return it as a dataframe'''
    headers = {'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    df = pd.read_html(str(soup))[0]

    return df


if __name__ =='__main__':
    pages = range(2, int(sys.argv[1]))
    url = f"https://twitchtracker.com/channels/viewership?page=1"

    # Scrape channel data
    print('Scraping channel information.')

    # First page
    df = parse_html(url)
    # Following pages
    for page in pages:
        print(page)
        new_df = parse_html(f"https://twitchtracker.com/channels/viewership?page={page}")
        df = df.append(new_df, ignore_index=True)
        time.sleep(1)

    # Remove and rename columns and rows as appropriate
    print('Parsing...')

    df.pop('Unnamed: 1')
    df = df.rename(columns={'Unnamed: 2': 'Username'})
    df = df.rename(columns={'Unnamed: 0': 'Id'})
    to_remove = df["Id"].str.contains('ads')
    df_toremove_index = df[to_remove].index
    df = df.drop(index=df_toremove_index)


    # Write the channel data to file
    df.to_csv(f'data/channels.csv')
    # Loop over usernames and get their game data
    for streamer in df['Username'].head(1).to_list():
        url = f"https://twitchtracker.com/{streamer.lower()}/games"
        game_df = parse_html(url)
        # Write the data to csv
        game_df.to_csv(f'data/games/{streamer}.csv')
