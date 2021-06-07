import os
import tweepy as tw
import pandas as pd
import geograpy
import os
from os.path import join
from twython import Twython
import os
import time

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

def get_streamer_data(streamer):
    consumer_key= 'RBAhyItP3hdDNBH9LpNPTfl4F'
    consumer_secret='DT0lHHLgNWqhIKlPCqtTw7E3jyIogDqU8u5PUL8lGSUosSSvV2' 
    access_token= '798115618243411968-RiWI7ZbAyZdCD2ZH7XQDHdYA2UTzvK8'
    access_token_secret= '3wK6v91wmQ3rlOpr0SEw4lnCUKm1NrypJqtNKEKfx7Nzf'
    python_tweets = Twython(consumer_key, consumer_secret)
    streamer_data=[]
#     time.sleep(60*15) #run every 15min
#     for outlet in news:
    streamer_data.append(python_tweets.get_user_timeline(screen_name=streamer, count=10))
    streamer_tweets = pd.DataFrame(streamer_data)
    return streamer_tweets

def get_streamer_data_filtered(streamer):
    data_streamer_filtered=[]
    for column in get_streamer_data(streamer):
        for row in get_streamer_data(streamer)[column]:
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
            created_at = row["created_at"]
            data_streamer_filtered.append({"id_new":id_new,"text":text,"url":url,"expanded_url":expanded_url,"name":name,"location":location,"followers_count":followers_count,"friends_count":friends_count,"listed_count":listed_count,"favourites_count":favourites_count,"profile_image_url":profile_image_url,"retweet_count":retweet_count,"source":source,"created_at":created_at})
    streamer_tweets = pd.DataFrame(data_streamer_filtered)
    return streamer_tweets