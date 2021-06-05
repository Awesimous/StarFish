import requests
from bs4 import BeautifulSoup
import pandas as pd

df = pd.read_csv('streamer_df')

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
            print(count)
            time.sleep(t)
        except:
            continue
    return df_all
usernames = df['username'].to_list()
parse_streams(usernames[:15]).to_csv(r'/Users/home/code/Awesimous/StarFish/notebooks/top100_streams', index=False)

