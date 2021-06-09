import pandas as pd
def games_dict():
    games_dict = {
    'WoW': ['MORE (Multiplayer online role-playing game)', 'Leslie Benzies, Simon Lashley, David Jones, Imran Sarwar, Billy Thomson', 2004 , 14 , '84%'],
    'Grand Theft Auto V': ['Action-Adventure Game', 'David Jones and Mike Dailly', 2013, 13, '95%'],
    'VALORANT': ['Tactical Shooter','Riot Games',2020, 16, '90%'],
    'Call of Duty': ['First-person Shooter', 'Activision, Treyarch, Infinity Ward, Raven Software, MORE', 2003, 18, '95%'],
    'Minecaft': ['Sandbox-Survival', ' Mojang', 2011, 10, ''],
    'Fortnite':['Survival', 'Epic games', 2017,12,'85%'],
    'League of Legends': ['MOBA (Multiplayer online battle arena)', 'Steve Feak, Mark Yetter, Tom Cadwell, Christina Norman, David Capurro, Rob Garrett', 2009, 11, '76%'],
    }
    return pd.DataFrame.from_dict(games_dict, orient='index', columns=['Category', 'Created by', 'Release Date', 'Recommended Age', 'Likes pct'])