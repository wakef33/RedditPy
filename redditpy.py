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

__version__ = 'RedditPy 0.9.0'

# TODO
# Better handle when no results are found
# Auto open html file
# Add -f to open config file
# Add -w for where to write html file to
# Fix login error handling

class RedditPy():
    '''
    Creates a list of saved links
    '''
    
    def __init__(self):
        self.conf_file = []
        self.saved_list = []
        self.reddit = None
    
    
    def read_conf(self):
        '''
        Get creds from conf file
        '''
        
        try:
            with open('redditpy.conf') as open_conf:
                # Creates a list of creds from conf file
                for i in open_conf:
                    settings_list = i.strip().split('=')
                    self.conf_file.append(settings_list[1])
        except IOError:    # redditpy.conf file not found
            print('Error: redditpy.conf not found')
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
    
    
    def get_id(self):
        '''
        Gets ids of saved links
        '''
        
        id_list = []
        for id_number in self.saved_list:
            id_list.append(id_number[0])
        return id_list
    
    
    def get_title(self):
        '''
        Gets titles of saved links
        '''
        
        title_list = []
        for title in self.saved_list:
            title_list.append(title[1])
        return title_list
    
    
    def get_permalink(self):
        '''
        Gets permalinks of saved links
        '''
        
        permalink_list = []
        for permalink in self.saved_list:
            permalink_list.append(permalink[2])
        return permalink_list
    
    
    def get_url(self):
        '''
        Gets urls of saved links
        '''
        
        url_list = []
        for url in self.saved_list:
            url_list.append(url[3])
        return url_list


def parse_saves(args_search, r, args_subreddit):
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
        write_html(hit_list_2)
    # Search for Title Only
    elif (args_search != None) and (args_subreddit == None):
        hit_list = []                       # List for match search strings
        for i in args_search:               # Loops through arguments for strings to match on
            for j in r.saved_list:          # Loops through saved list
                if i in j[1]:               # If string matches in title of saved list
                    hit_list.append(j)      # Append to hit_list
        write_html(hit_list)
    # Search for Subreddit Only
    elif (args_search == None) and (args_subreddit != None):
        hit_list = []                       # List for match subreddits
        for i in args_subreddit:            # Loops through arguments for subreddit to match on
            for j in r.saved_list:          # Loops through saved list
                if i in j[4]:               # If string matches subreddit in saved list
                    hit_list.append(j)      # Append to hit_list
        write_html(hit_list)
    # Write Everything
    else:
        write_html(r.saved_list)


def write_html(search_list):
    '''
    Creates html file for viewing
    '''
    
    if len(search_list) == 0:
        print("No Matches")
        raise SystemExit()
    try:
        with open('redditpy.html', 'w') as open_html:
            for i in search_list:
                # i[0] = ID Number
                # i[1] = Post Title
                # i[2] = Permalink
                # i[3] = URL
                # i[4] = Subreddit
                subreddit = i[2][3:].split("/")
                open_html.write(str(i[0]) + ": " + i[4] + " --- <a href=https://www.reddit.com/" + i[2] + ">" +  i[1] + "</a> --- <a href=" + i[3] + ">Source</a><br />\n")
    except IOError:
        print('Error: Could not write to file')
        raise SystemExit()


def thread_loop(args_search, r, thread_check, args_number, args_subreddit):
    '''
    Creates threads to indicate the
    process is still parsing data
    '''
    
    if thread_check == 'Download':
        args_number_list = [args_number]
        t2 = threading.Thread(target=r.download_saves, args=(args_number_list), name='t2')
        t2.start()
    elif thread_check == 'Parse':
        t2 = threading.Thread(target=parse_saves, args=(args_search, r, args_subreddit), name='t2')
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
    
    parser = argparse.ArgumentParser(description='Presents information about Reddit user\'s saved links')
    parser.add_argument('-s', '--search', dest='search', help='Search for keyword in title', required=False, nargs='*', type=str)
    parser.add_argument('-r', '--subreddit', dest='subreddit', help='Search only specified subreddits', required=False, nargs='*', type=str)
    parser.add_argument('-n', '--number', dest='number', help='Number of save links to search through', required=False, nargs='?', default=27, type=int)
    parser.add_argument('-c', '--clean', dest='clean', help='Removes redditpy.html file', required=False, action='store_true')
    parser.add_argument('-v', '--version', dest='version', help='Prints version number', required=False, action='store_true')
    args = parser.parse_args()
    
    # Prints version then exits
    if args.version:
        print(__version__)
        raise SystemExit()
    
    # Removes html file
    if args.clean:
        try:
            os.remove('redditpy.html')
            print("Removed redditpy.hmtl")
            raise SystemExit()
        except IOError:
            print("Error: Could not remove file")
            raise SystemExit()
    
    # Creates RedditPy object
    r = RedditPy()
    r.read_conf()
    r.login(r.conf_file[0], r.conf_file[1], r.conf_file[2], r.conf_file[3], r.conf_file[4])
    
    # Multithreading Download
    t1 = threading.Thread(target=thread_loop, args=(args.search, r, 'Download', args.number, args.subreddit), name='t1')
    t1.start()
    t1.join()
    
    # Multithreading Parse
    t1 = threading.Thread(target=thread_loop, args=(args.search, r, 'Parse', args.number, args.subreddit), name='t1')
    t1.start()
    t1.join()


if __name__ == '__main__':
    main()
