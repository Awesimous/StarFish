import requests
from bs4 import BeautifulSoup
import pandas as pd

df = pd.read_csv('streamer_df_clean')

def time_assignment(x):
    '''Support function to classify streams by time when they are on air'''
    midnight = 24
    morning = 6
    noon = 12
    evening = 18
    if morning <= x.hour < noon:
        return 1
    elif noon <= x.hour < evening:
        return 2
    elif evening <= x.hour < midnight:
        return 3
    else:
        return 0


def parse_streams(usernames):
    import time
    t=1
    count = 0
    df_all = pd.DataFrame(columns=['Stream', 'Duration', 'AVG Viewers', 'MAX Viewers', 'Followers Gain', 'Live Views', 'Title', 'Games', 'User'])
    for user in usernames:
        count += 1
        url = f"https://twitchtracker.com/{user}/streams"
        headers = {'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        try:
            df = pd.read_html(str(soup))[0]
            df['User'] = f'{user}'
            df_all = pd.concat([df_all, df])
            if count % 10 == 0:
                print(count)
            time.sleep(t)
        except:
            if count % 10 == 0:
                print(count)
            continue
    df_all = df_all.fillna(0)
    df_all['Stream'] = pd.to_datetime(df_all['Stream'])
    df_all['Duration'] = df_all['Duration'].apply(lambda x: int(x))
    df_all['AVG Viewers'] = df_all['AVG Viewers'].apply(lambda x: int(x))
    df_all['MAX Viewers'] = df_all['MAX Viewers'].apply(lambda x: int(x))
    df_all['Followers Gain'] = df_all['Followers Gain'].apply(lambda x: int(x))
    df_all['Live Views'] = df_all['Live Views'].apply(lambda x: int(x))
    new_dates, new_times = zip(*[(d.date(), d.time()) for d in df_all['Stream']])
    df_clean = df_all.assign(new_date=new_dates, new_time=new_times)
    df_clean = df_clean[['User', 'new_date', 'new_time', 'Duration', 'AVG Viewers', 'MAX Viewers', 'Followers Gain', 'Live Views', 'Title']]
    df_clean['daytime_classifier'] = df_clean['new_time'].apply(lambda x: time_assignment(x))    
    return df_clean
usernames = df['username'].to_list()
#parse_streams(usernames[:150]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_1', index=False)
#parse_streams(usernames[150:300]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_2', index=False)
#parse_streams(usernames[300:450]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_3', index=False)
#parse_streams(usernames[450:600]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_4', index=False)
#parse_streams(usernames[600:750]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_5', index=False)
#parse_streams(usernames[750:900]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_6', index=False)
#parse_streams(usernames[900:1050]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_7', index=False)
#parse_streams(usernames[1050:1300]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_8', index=False)
#parse_streams(usernames[1300:1450]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_9', index=False)
#parse_streams(usernames[1450:1600]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_10', index=False)
#parse_streams(usernames[1600:1750]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_11', index=False)
#parse_streams(usernames[1750:1900]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_12', index=False)
#parse_streams(usernames[1900:2050]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_13', index=False)
parse_streams(usernames[2050:2200]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_14', index=False)
parse_streams(usernames[2200:2450]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top_2500_15', index=False)
