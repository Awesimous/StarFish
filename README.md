# Starfish

A twitch broadcaster information dashboard. A small broadcaster ranking and highlighting tool.

Contents
----
- Links
- Development Environment Setup
- Features selected for
- Milestones

### Links
- [Trello](https://trello.com/b/4jGmUJGH/starfish)

### API Notes

- unfortunately, get broadcaster subscriptions requires the broadcaster's authorization.

###### Sorting
- search categories
- get channel information
- search channels
- get stream tags
- get all stream tags
- get channel teams
- get teams
- get top games
- get games

###### By Streamer
- get videos (video ids, user id, game id)
- get bits leaderboard (by channel)

- get hype train events
- (Extension and game analytics)

TODO: understand relationship between "games" and "categories". See: get streams for example. What are game_id and game_name, for a knitting stream?

### Development Environment Setup

From an environment already set up with the lewagon pyenv:

    pyenv global 3.8.6
    pyenv virtualenv starfish
    pyenv activate starfish
    pip install -r requirements.txt

It should say `[starfish]` at the right end of your shell prompt.


### Milestones

| Stage | Description |
| ---- | ---- |
| MVP | A dashboard collating scraped and api data, usefully interpreted |