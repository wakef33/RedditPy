#!/usr/bin/env python3
'''
RedditPy downloads user's saved
links and allows user to parse/backup
based on strings and/or subreddit.
'''

import os
import time
import praw
import threading
import argparse
import pickle

__version__ = 'RedditPy 0.9.9'


class RedditPy():
    '''
    Creates a list of saved links
    '''
    
    def __init__(self, read_file, search_number, backup):
        self.conf_file = []
        self.saved_list = []
        self.read_file = read_file
        self.search_number = search_number
        self.backup = backup
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
    
    
    def login(self, reddit_user_agent, reddit_client_id, reddit_client_secret, reddit_username, reddit_password):
        '''
        Logs into account
        '''
        
        # Try to login using information in config file
        login_attempt = True
        while login_attempt:
            print("Logging In...")
            try:
                self.reddit = praw.Reddit(
                    user_agent=reddit_user_agent,
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    username=reddit_username,
                    password=reddit_password)
                print("Logged In")
                login_attempt = False
            except:
                print("Wrong username or password")
                raise SystemExit()
    
    
    def thread_loop(self):
        '''
        Creates threads to indicate the
        process is still parsing data
        '''
        
        t1 = threading.Thread(target=self.download_saves, name='t1')
        t1.start()
        
        while True:
            print('Downloading -', end='\r', flush=True)
            time.sleep(0.3)
            print('Downloading \\', end='\r', flush=True)
            time.sleep(0.3)
            print('Downloading |', end='\r', flush=True)
            time.sleep(0.3)
            print('Downloading /', end='\r', flush=True)
            time.sleep(0.3)
            if not t1.isAlive():
                print("Complete     ")
                break
    
    
    def download_saves(self):
        '''
        Downloads saved links from Reddit
        '''
        
        saved_links = self.reddit.user.me().saved(limit=self.search_number)    # Gets list of user's saved links
        
        if self.backup != False:
            try:
                with open('redditpy.bak', 'ab') as write_backup:
                    pickle.dump(saved_links, write_backup)
            except IOError:
                print('Error: Could not write to file')
        
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
        
        # if reading from backup file
        if self.read_file != False:
            try:
                with open('redditpy.bak', 'rb') as open_local:
                    pickle_file = pickle.load(open_local)
                    for link in pickle_file:
                        subreddit = link.permalink[3:].split("/", 1)[0]
                        temp_list = []
                        temp_list.append(i)                 # Append ID
                        temp_list.append(link.title)        # Append Title
                        temp_list.append(link.permalink)    # Append Permalink
                        temp_list.append(link.url)          # Append URL
                        temp_list.append(subreddit)         # Append Subreddit
                        self.saved_list.append(temp_list)   # Temp List to Actual List
                        i = i + 1
            except IOError:
                print('Error: Could not read file')
    
    
    def parse_saves(self, args_search, args_subreddit, html_file):
        '''
        Creates list from saved
        list that matched a string
        '''
        
        # Search for Subreddit and Title
        if (args_search != None) and (args_subreddit != None):
            hit_list_1 = []                     # List for matched subreddits
            for i in args_subreddit:            # Loops through arguments for subreddits to match on
                for j in self.saved_list:       # Loops through saved list
                    if i in j[4]:               # If string matches subreddit in saved list
                        hit_list_1.append(j)    # Append to hit_list_1
            hit_list_2 = []                     # List for match search strings
            for i in args_search:               # Loops through arguments for strings to match on
                for j in hit_list_1:            # Loops through hit_list_1
                    if i in j[1]:               # If string matches in title found in hit_list_1
                        hit_list_2.append(j)
            self.write_html(hit_list_2, html_file)
        # Search for Title Only
        elif (args_search != None) and (args_subreddit == None):
            hit_list = []                       # List for match search strings
            for i in args_search:               # Loops through arguments for strings to match on
                for j in self.saved_list:       # Loops through saved list
                    if i in j[1]:               # If string matches in title of saved list
                        hit_list.append(j)      # Append to hit_list
            self.write_html(hit_list, html_file)
        # Search for Subreddit Only
        elif (args_search == None) and (args_subreddit != None):
            hit_list = []                       # List for match subreddits
            for i in args_subreddit:            # Loops through arguments for subreddit to match on
                for j in self.saved_list:       # Loops through saved list
                    if i in j[4]:               # If string matches subreddit in saved list
                        hit_list.append(j)      # Append to hit_list
            self.write_html(hit_list, html_file)
        # Write Everything
        else:
            self.write_html(self.saved_list, html_file)
    
    
    def write_html(self, search_list, html_file):
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


def main():
    '''
    Starts main program
    '''
    
    parser = argparse.ArgumentParser(description='Parses Reddit user\'s saved links')
    parser.add_argument(
            '-s', '--search',
            dest='search',
            help='Search for keyword in title',
            required=False, nargs='*', type=str)
    parser.add_argument(
            '-S', '--subreddit',
            dest='subreddit',
            help='Search only specified subreddits',
            required=False, nargs='*', type=str)
    parser.add_argument(
            '-n', '--number',
            dest='number',
            help='Number of save links to search through',
            required=False, nargs='?', default=100, type=int)
    parser.add_argument(
            '-c', '--config',
            dest='config',
            help='Config file to read from',
            required=False, nargs='?', default='redditpy.conf', type=str)
    parser.add_argument(
            '-w', '--write',
            dest='write',
            help='Write html file to location',
            required=False, nargs='?', default='redditpy.html', type=str)
    parser.add_argument(
            '-r', '--read',
            dest='read',
            help='Read from backup file',
            required=False, action='store_true')
    parser.add_argument(
            '-b', '--backup',
            dest='backup',
            help='Backup saved links to location',
            required=False, action='store_true')
    parser.add_argument(
            '-v', '--version',
            dest='version',
            help='Print version number',
            required=False, action='store_true')
    args = parser.parse_args()
    
    # Prints version then exits
    if args.version:
        print(__version__)
        raise SystemExit()
    
    # Checks if args.number > 1000
    if args.number > 1000:
        print("Reddit caps at 1000. Searching last 1000 saved links...")
        args.number = 1000
    
    # Creates RedditPy object
    r = RedditPy(args.read, args.number, args.backup)
    r.read_conf(args.config)
    r.login(r.conf_file[0], r.conf_file[1], r.conf_file[2], r.conf_file[3], r.conf_file[4])
    
    # Multi-threaded Download
    r.thread_loop()
    
    # Parse Saved Links
    r.parse_saves(args.search, args.subreddit, args.write)


if __name__ == '__main__':
    main()
