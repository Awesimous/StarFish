# Starfish

A twitch broadcaster information dashboard. A small broadcaster ranking and highlighting tool.

## Contents
- Links
- API Notes
- TODO
- Development Environment Setup
- Milestones


## Links
- [Trello](https://trello.com/b/4jGmUJGH/starfish)
- [Google Cloud Cheatsheet](https://github.com/gregsramblings/google-cloud-4-words)
- [Shared Notion Text Document](https://www.notion.so/Starfish-a4093726e4a34a5580738ce658fc4a22)


## API Notes
- unfortunately, get broadcaster subscriptions (the users) requires the broadcaster's authorization. This could be done with an app with the broadcaster as a user.

__Possibly__: dataframes for broadcasters, teams, games (times and engagement)

Broadcasters:
broadcaster_id (index by) | display_name | broadcaster_language | team_id | team_display_name | team_name | team_updated_at | team_created_at | team_info
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |

- broadcaster_id (index by)
- display_name
- broadcaster_language
- team_id
- team_display_name
- team_name
- team_updated_at
- team_created_at
- team_info


###### Sorting
- search channels; `display_name` -> `id` (match to`broadcaster_id`)
- get channel information; keep in mind `broadcaster_name` != `broadcaster_id`
- get channel teams; per team: `id` + `team_display_name` + `team_name` + `updated_at` + `info`
- get teams; `name` and `id`(from above) returns `users[id]`
- get top games; get top 100 + pagination. How plugged in or niche are any streamers?
- get games; for connecting a broadcaster lookup with the last thing they streamed through `id` and `name` (game id and name)
- get all stream tags; pivotal
- get stream tags
- search categories; for searching games or categories. Noisy results.


###### By Streamer
- get videos (video ids, user id, game id); aggregate information on videos by topic and language. "What kind of streams are XXXX streams?"
- get streams; How active are certain timeframes for certain languages.


## TODOs
- !TODO: sift through all stream tags and read the english version. This will be key. Remember get stream tags has an`is_auto` = False for some streams. Find some.

- TODO: understand relationship between "games" and "categories". See: get streams for example. What are game_id and game_name, for a knitting stream? `game_name` is the game last streamed

- TODO: And knitting streamers?


## Development Environment Setup
With an environment already set up with the lewagon pyenv, from the starfish directory:

    pyenv global 3.8.6
    pyenv virtualenv starfish
    pyenv activate starfish
    pip install --upgrade pip
    pip install -r requirements.txt
    pyenv global lewagon

It should say `[starfish]` at the right end of your shell prompt.


## Milestones

| Stage | Description |
| ---- | ---- |
| MVP | A dashboard collating scraped and api data, usefully interpreted |
