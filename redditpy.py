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

__version__ = 'RedditPy 1.1.0'


class RedditPy():
    '''
    Creates a list of saved links from Reddit
    user's account. Methods to parse/save links.
    '''
    
    def __init__(self, read_file, search_number):
        '''
        Initialize a RedditPy instance.

        :param read_file: Backup file to read from. Default redditpy.bak.
        :param search_number: Number of saved links to parse through.
        '''
        
        self.conf_file = []
        self.saved_list = []
        self.read_file = read_file
        self.search_number = search_number
        self.reddit = None
    
    
    def read_conf(self, config):
        '''
        Gets creds from RedditPy config file.

        :param config: The location of the configuration file. Default redditpy.conf.
        '''
        
        try:
            with open(config) as open_conf:
                # Creates a list of creds from conf file
                for i in open_conf:
                    settings_list = i.strip().split('=')
                    self.conf_file.append(settings_list[1])
        except IOError:    # redditpy.conf file not found
            raise SystemExit('Error: {} not found'.format(config))
    
    
    def login(self):
        '''
        Logs into user's Reddit account using praw.
        '''
        
        # Try to login using information in config file
        login_attempt = True
        while login_attempt:
            print("Logging In...")
            try:
                self.reddit = praw.Reddit(
                    user_agent=self.conf_file[0],
                    client_id=self.conf_file[1],
                    client_secret=self.conf_file[2],
                    username=self.conf_file[3],
                    password=self.conf_file[4])
                print("Logged In")
                login_attempt = False
            except:
                raise SystemExit("Wrong username or password")
    
    
    def backup(self, backup_file):
        '''
        Backup saved links to a file using a pickle.
        
        :param backup_file: The location to backup the saved links to. Default redditpy.bak.
        '''
        
        # Test if backup file already exists
        file_test = False
        file_test_warning = False
        if os.path.isfile(backup_file) == True:
            file_test = True
            file_test_warning = True
            file_test_number = 0
        while file_test:
            if os.path.isfile(backup_file + str(file_test_number)) == True:
                file_test_number = file_test_number + 1
            else:
                file_test = False
        
        # If backup file exists, warns user and changes name
        if file_test_warning == True:
            backup_file = backup_file + str(file_test_number)
            print("Backup file already exists. Creating {} instead.".format(backup_file))
        
        try:
            with open(backup_file, 'wb') as write_backup:
                pickle.dump(self.saved_list, write_backup)
                print("Saved links backed up to {}".format(backup_file))
                raise SystemExit()
        except IOError:
            raise SystemExit('Error: Could not write to {}'.format(backup_file))
    
    
    def thread_loop(self):
        '''
        Creates a new thread to indicate to the user that
        the download is still occuring. Calls download_save method.
        '''
        
        t1 = threading.Thread(target=self.download_saves, name='t1')
        t1.start()
        
        while True:
            print('Downloading -', end='\r', flush=True)
            time.sleep(0.2)
            print('Downloading \\', end='\r', flush=True)
            time.sleep(0.2)
            print('Downloading |', end='\r', flush=True)
            time.sleep(0.2)
            print('Downloading /', end='\r', flush=True)
            time.sleep(0.2)
            if not t1.isAlive():
                print("Complete     ")
                break
    
    
    def download_saves(self):
        '''
        Downloads saved links from user's Reddit account using praw.
        '''
        
        saved_links = self.reddit.user.me().saved(limit=self.search_number)    # Gets list of user's saved links
        
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
            i += 1
        
        # if reading from backup file
        if self.read_file != None:
            try:
                with open(self.read_file, 'rb') as open_local:
                    pickle_file = pickle.load(open_local)
                    for saved_list in pickle_file:
                        self.saved_list.append(saved_list)
                        i += 1
            except IOError:
                print('Error: Could not read {}'.format(self.read_file))
    
    
    def parse_saves(self, args_search, args_subreddit, html_file):
        '''
        Creates a list from user's saved links that matched a string.

        :param args_search: String to match against Reddit post title.
        :param args_subreddit: String to match against Reddit subreddit.
        :param html_file: Location to save the html file to. Object is passed to write_html(). Default redditpy.html.
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
        Creates html file to easily view with a web browser.

        :param search_list: The list that matched against parse_saves().
        :param html_file: Location to save the html file to. Default redditpy.html.
        '''
        
        if len(search_list) == 0:
            raise SystemExit("No Matches")
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
            raise SystemExit("Error: Could not write to {}".format(html_file))


def main():
    '''
    Starts main program.
    '''
    
    parser = argparse.ArgumentParser(description='RedditPy downloads user\'s saved links and allows user to parse/backup based on strings and/or subreddit.')
    parser.add_argument(
            '-s', '--search',
            dest='search',
            help='Search for keyword in title.',
            required=False, nargs='*', type=str)
    parser.add_argument(
            '-S', '--subreddit',
            dest='subreddit',
            help='Search only specified subreddits.',
            required=False, nargs='*', type=str)
    parser.add_argument(
            '-n', '--number',
            dest='number',
            help='Number of save links to parse through. Default 100 links.',
            required=False, nargs='?', default=100, type=int)
    parser.add_argument(
            '-c', '--config',
            dest='config',
            help='Config file to read from. Default redditpy.conf.',
            required=False, nargs='?', default='redditpy.conf', type=str)
    parser.add_argument(
            '-w', '--write',
            dest='write',
            help='Write html file to specific location. Default redditpy.html.',
            required=False, nargs='?', default='redditpy.html', type=str)
    parser.add_argument(
            '-r', '--read',
            dest='read',
            help='Read from backup file. Default redditpy.bak.',
            required=False, nargs='?', const='redditpy.bak', type=str)
    parser.add_argument(
            '-b', '--backup',
            dest='backup',
            help='Backup saved links to specific location. Default redditpy.bak.',
            required=False, nargs='?', const='redditpy.bak', type=str)
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
    r = RedditPy(args.read, args.number)
    r.read_conf(args.config)
    r.login()
    
    # Multi-threaded Download
    r.thread_loop()
    
    # Backup saved links if requested
    if args.backup != None:
        r.backup(args.backup)
    
    # Parse Saved Links
    r.parse_saves(args.search, args.subreddit, args.write)


if __name__ == '__main__':
    main()
