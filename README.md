# RedditPy

RedditPy downloads user's saved links and allows
user to parse/backup based on strings and/or subreddit.

## Requirements

RedditPy was built using Python 3.7.2 and praw 6.1.1.

```
pip3 install praw
```

## Example

```python
usage: redditpy.py [-h] [-s [SEARCH [SEARCH ...]]]
                   [-S [SUBREDDIT [SUBREDDIT ...]]] [-n [NUMBER]]
                   [-c [CONFIG]] [-w [WRITE]] [-r [READ]] [-b [BACKUP]] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -s [SEARCH [SEARCH ...]], --search [SEARCH [SEARCH ...]]
                        Search for keyword in title.
  -S [SUBREDDIT [SUBREDDIT ...]], --subreddit [SUBREDDIT [SUBREDDIT ...]]
                        Search only specified subreddits.
  -n [NUMBER], --number [NUMBER]
                        Number of save links to parse through. Default 100
                        links.
  -c [CONFIG], --config [CONFIG]
                        Config file to read from. Default redditpy.conf.
  -w [WRITE], --write [WRITE]
                        Write html file to specific location. Default
                        redditpy.html.
  -r [READ], --read [READ]
                        Read from backup file. Default redditpy.bak.
  -b [BACKUP], --backup [BACKUP]
                        Backup saved links to specific location. Default
                        redditpy.bak.
  -v, --version         Print version number


./reddit.py -n 500 -S LearnPython -s praw
```
