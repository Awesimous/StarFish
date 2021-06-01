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