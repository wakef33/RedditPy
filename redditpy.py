#!/usr/bin/env python3
'''
RedditPy downloads user's saved
links and allows user to parse
based on strings and/or subreddit.
'''

import os
import time
import praw
import threading
import argparse

__version__ = 'RedditPy 0.9.2'

# TODO
# Auto open html file
# Fix login error handling

class RedditPy():
    '''
    Creates a list of saved links
    '''
    
    def __init__(self):
        self.conf_file = []
        self.saved_list = []
        self.reddit = None
    
    
    def read_conf(self, config):
        '''
        Get creds from conf file
        '''
        
        try:
            with open(config) as open_conf:
                # Creates a list of creds from conf file
                for i in open_conf:
                    settings_list = i.strip().split('=')
                    self.conf_file.append(settings_list[1])
        except IOError:    # redditpy.conf file not found
            print('Error: {} not found'.format(config))
            raise SystemExit()
        return self.conf_file
    
    
    def login(self, reddit_user_agent, reddit_client_id, reddit_client_secret, reddit_username, reddit_password):
        '''
        Logs into account
        '''
        
        # Try to login or sleep/wait until logged in, or exit if user/pass wrong
        NotLoggedIn = True
        while NotLoggedIn:
            print("Logging In...")
            try:
                self.reddit = praw.Reddit(
                    user_agent=reddit_user_agent,
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    username=reddit_username,
                    password=reddit_password)
                print("Logged In")
                NotLoggedIn = False
            except praw.errors.InvalidUserPass:
                print("Wrong username or password")
                raise SystemExit()
            except Exception as err:
                print(err)
                print("Unknown Error")
                raise SystemExit()
    
    
    def download_saves(self, number_links):
        '''
        Downloads saved links from Reddit
        '''
        
        print("Grabbing Saved Links...")
        saved_links = self.reddit.user.me().saved(limit=number_links)    # Gets list of user's saved links
        
        i = 0
        for link in saved_links:
            subreddit = link.permalink[3:].split("/", 1)[0]
            temp_list = []
            temp_list.append(i)                 # Append ID
            temp_list.append(link.title)        # Append Title
            temp_list.append(link.permalink)    # Append Permalink
            temp_list.append(link.url)          # Append URL
            temp_list.append(subreddit)         # Append Subreddit
            self.saved_list.append(temp_list)   # Temp List to Actual List
            i = i + 1


def parse_saves(args_search, r, args_subreddit, html_file):
    '''
    Creates list from saved
    list that matched a string
    '''
    
    print("Parsing Saved Links...")
    
    # Search for Subreddit and Title
    if (args_search != None) and (args_subreddit != None):
        hit_list_1 = []                     # List for matched subreddits
        for i in args_subreddit:            # Loops through arguments for subreddits to match on
            for j in r.saved_list:          # Loops through saved list
                if i in j[4]:               # If string matches subreddit in saved list
                    hit_list_1.append(j)    # Append to hit_list_1
        hit_list_2 = []                     # List for match search strings
        for i in args_search:               # Loops through arguments for strings to match on
            for j in hit_list_1:            # Loops through hit_list_1
                if i in j[1]:               # If string matches in title found in hit_list_1
                    hit_list_2.append(j)
        write_html(hit_list_2, html_file)
    # Search for Title Only
    elif (args_search != None) and (args_subreddit == None):
        hit_list = []                       # List for match search strings
        for i in args_search:               # Loops through arguments for strings to match on
            for j in r.saved_list:          # Loops through saved list
                if i in j[1]:               # If string matches in title of saved list
                    hit_list.append(j)      # Append to hit_list
        write_html(hit_list, html_file)
    # Search for Subreddit Only
    elif (args_search == None) and (args_subreddit != None):
        hit_list = []                       # List for match subreddits
        for i in args_subreddit:            # Loops through arguments for subreddit to match on
            for j in r.saved_list:          # Loops through saved list
                if i in j[4]:               # If string matches subreddit in saved list
                    hit_list.append(j)      # Append to hit_list
        write_html(hit_list, html_file)
    # Write Everything
    else:
        write_html(r.saved_list, html_file)


def write_html(search_list, html_file):
    '''
    Creates html file for viewing
    '''
    
    if len(search_list) == 0:
        print("No Matches")
        raise SystemExit()
    try:
        with open(html_file, 'w') as open_html:
            for i in search_list:
                # i[0] = ID Number
                # i[1] = Post Title
                # i[2] = Permalink
                # i[3] = URL
                # i[4] = Subreddit
                subreddit = i[2][3:].split("/")
                open_html.write(str(i[0]) + ": {} --- <a href=https://www.reddit.com/{}>{}</a> --- <a href={}>Source</a><br />\n".format(i[4], i[2], i[1], i[3]))
    except IOError:
        print('Error: Could not write to file')
        raise SystemExit()


def thread_loop(r, args_number):
    '''
    Creates threads to indicate the
    process is still parsing data
    '''
    
    args_number_list = [args_number]
    t2 = threading.Thread(target=r.download_saves, args=(args_number_list), name='t2')
    t2.start()
    
    while True:
        print('Running -', end='\r', flush=True)
        time.sleep(0.3)
        print('Running \\', end='\r', flush=True)
        time.sleep(0.3)
        print('Running |', end='\r', flush=True)
        time.sleep(0.3)
        print('Running /', end='\r', flush=True)
        time.sleep(0.3)
        if not t2.isAlive():
            print("Complete   ")
            break


def main():
    '''
    Starts main program
    '''
    
    parser = argparse.ArgumentParser(description='Parses Reddit user\'s saved links')
    parser.add_argument('-s', '--search', dest='search', help='Search for keyword in title', required=False, nargs='*', type=str)
    parser.add_argument('-r', '--subreddit', dest='subreddit', help='Search only specified subreddits', required=False, nargs='*', type=str)
    parser.add_argument('-n', '--number', dest='number', help='Number of save links to search through', required=False, nargs='?', default=100, type=int)
    parser.add_argument('-f', '--file', dest='config', help='Config file', required=False, nargs='?', default='redditpy.conf', type=str)
    parser.add_argument('-w', '--write', dest='write', help='Write html file to location', required=False, nargs='?', default='redditpy.html', type=str)
    parser.add_argument('-c', '--clean', dest='clean', help='Removes html file. Use with \'-w\' to specify html file', required=False, action='store_true')
    parser.add_argument('-v', '--version', dest='version', help='Prints version number', required=False, action='store_true')
    args = parser.parse_args()
    
    # Prints version then exits
    if args.version:
        print(__version__)
        raise SystemExit()
    
    # Removes html file
    if args.clean:
        try:
            os.remove(args.write)
            print("Removed {}".format(args.write))
            raise SystemExit()
        except IOError:
            print("Error: Could not remove {}".format(args.write))
            raise SystemExit()
    
    # Creates RedditPy object
    r = RedditPy()
    r.read_conf(args.config)
    r.login(r.conf_file[0], r.conf_file[1], r.conf_file[2], r.conf_file[3], r.conf_file[4])
    
    # Multithreading Download
    t1 = threading.Thread(target=thread_loop, args=(r, args.number), name='t1')
    t1.start()
    t1.join()
    
    # Parse Saved Links
    parse_saves(args.search, r, args.subreddit, args.write)


if __name__ == '__main__':
    main()
