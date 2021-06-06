#!usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from random import uniform


def parse_html(url):
    '''Read a webpage and return it as a dataframe'''
    headers = {'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    df = pd.read_html(str(soup))[0]

    return df

def get_channels_data(n_pages):
    pages = range(1, int(n_pages) + 1)
    print('Scraping channel information.')

    channels_df = pd.DataFrame()
    for page in pages:
        print(f'{page}/{n_pages}')
        # Get channel overviwew data
        df = parse_html(f"https://twitchtracker.com/channels/viewership?page={page}")
        channels_df = channels_df.append(df, ignore_index = True)
        time.sleep(uniform(1,4))

    # Remove and rename channel columns and rows as appropriate
    print('Parsing...')

    channels_df.pop('Unnamed: 1')
    channels_df = channels_df.rename(columns={'Unnamed: 2': 'Username'})
    channels_df = channels_df.rename(columns={'Unnamed: 0': 'Id'})
    to_remove = channels_df["Id"].str.contains('ads')
    df_toremove_index = channels_df[to_remove].index
    channels_df = channels_df.drop(index=df_toremove_index)

    return channels_df


def get_subs_data(n_pages):
    pages = range(1, int(n_pages) + 1)
    print('Scraping subscriptions information.')

    subs_df = pd.DataFrame()
    for page in pages:
        print(f'{page}/{n_pages}')
        # Get subs page
        df = parse_html('https://twitchtracker.com/subscribers?page={page}')
        subs_df = subs_df.append(df, ignore_index = True)
        time.sleep(uniform(1,4))


    return subs_df


def get_games_data(channels_data):
    for i, streamer in enumerate(channels_data['Username'].to_list()):
        url = f"https://twitchtracker.com/{streamer.lower()}/games"
        try:
            game_df = parse_html(url)
        except ValueError:
            print(f'ValueError at {i}: {streamer}')
            continue
        # Write the data to csv
        time.sleep(uniform(1,4))
        game_df.to_csv(f'data/games/{streamer}.csv')



if __name__ =='__main__':
    # Define the range of channels and subscribers pages to scrape
    #n_pages = input('How many pages would you like to scrape? ')

    # Write the channel, game, and subs data to file
    channels = get_channels_data(50)
    channels.to_csv(f'data/channels.csv')
    #channels = pd.read_csv('data/channels.csv')
    get_games_data(channels)
    get_subs_data(125).to_csv('data/subs.csv')


