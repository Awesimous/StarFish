import tweepy as tw
import pandas as pd
import geograpy
from twython import Twython
import streamlit as st
import os



def twitter_viewer_locations(consumer_key, consumer_secret, access_token,access_token_secret, user, date, item_count):
    '''Takes secrets, username on twitter and starting date (format yyyy-mm-dd)'''
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    new_search = f"@{user}"
    date_since = f"{date}"

    tweets = tw.Cursor(api.search,
                               q=new_search,
                               lang="en",
                               since=date_since).items(item_count)
    users_locs = [[tweet.user.screen_name, tweet.user.location] for tweet in tweets]
    tweet_text = pd.DataFrame(data=users_locs,
                        columns=['user', "location"])
    locations = ' '.join(tweet_text['location'].to_list())
    places = geograpy.get_geoPlace_context(text = locations)
    frequent_locations = {'cities': places.cities, 'countries': places.countries}
    return frequent_locations

#### Twitter limitation
#Limit of 100,000 requests per day to the /statuses/user_timeline endpoint, in addition to existing user-level and app-level rate limits. This limit is applied on a per-application basis, meaning that a single developer app can make up to 100,000 calls during any single 24-hour period.
#This method can only return up to 3,200 of a user's most recent Tweets. Native retweets of other statuses by the user is included in this total, regardless of whether include_rts is set to false when requesting this resource.
#- We can just retrieve 200 tweets/request
#- 900 tweets 15 min
#- 100000 in 24h


def get_streamer_data(consumer_key, consumer_secret, access_token, access_token_secret, streamer):
    python_tweets = Twython(consumer_key, consumer_secret)
    streamer_data=[]
#     time.sleep(60*15) #run every 15min
#     for outlet in news:
    streamer_data.append(python_tweets.get_user_timeline(screen_name=streamer, count=10))
    streamer_tweets = pd.DataFrame(streamer_data)
    return streamer_tweets

@st.cache
def get_streamer_data_filtered(streamer):
    CONSUMER_KEY= os.environ.get('CONSUMER_KEY')
    CONSUMER_SECRET=os.environ.get('CONSUMER_SECRET')
    ACCESS_TOKEN=os.environ.get('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET=os.environ.get('ACCESS_TOKEN_SECRET')
    print(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    data_streamer_filtered=[]
    for column in get_streamer_data(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN, ACCESS_TOKEN_SECRET,streamer):
        for row in get_streamer_data(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN, ACCESS_TOKEN_SECRET, streamer)[column]:
            id_new = row["id"]
            text = row["text"]
            try:
                url = row["entities"]["urls"][0]["url"]
            except:
                url =""
            try:
                expanded_url = row["entities"]["urls"][0]["expanded_url"]
            except:
                expanded_url =""
            name = row["user"]["name"]
            location = row["user"]["location"]
            followers_count = row["user"]["followers_count"]
            friends_count = row["user"]["friends_count"]
            listed_count = row["user"]["listed_count"]
            favourites_count = row["user"]["favourites_count"]
            profile_image_url = row["user"]["profile_image_url"]
            retweet_count= row["retweet_count"]
            source = row["source"]
            created_at = row["created_at"].strftime('%Y-%m-%d %H:%M')
            data_streamer_filtered.append({"Id_new":id_new,"Text":text,"Url":url,"Expanded_url":expanded_url,"Name":name,"Location":location,"Followers_count":followers_count,"Friends_count":friends_count,"Listed_count":listed_count,"Favourites_count":favourites_count,"Profile_image_url":profile_image_url,"Retweet_count":retweet_count,"Source":source,"Created_at":created_at})
    streamer_tweets = pd.DataFrame(data_streamer_filtered)
    streamer_tweets['Username'] = streamer 
    return streamer_tweets
