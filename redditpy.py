#!/usr/bin/env python3
'''
Quickly gets various information from
Reddit account.
'''

import os
import time
import praw
import threading
import argparse

__version__ = 'RedditPy 0.7.0'


class RedditPy():
    '''
    Creates a list of saved links
    '''
    
    def __init__(self, number_links):
        self.saved_list = []
        conf_list = read_conf()
        reddit_user_agent, reddit_client_id, reddit_client_secret, reddit_username, reddit_password = conf_list[0], conf_list[1], conf_list[2], conf_list[3], conf_list[4]
        reddit = login(reddit_user_agent, reddit_client_id, reddit_client_secret, reddit_username, reddit_password)     # Logs in with User Creds
        print("Grabbing Saved Links")
        saved_links = reddit.user.me().saved(limit=number_links)    # Gets list of user's saved links
        
        i = 0
        for link in saved_links:
            temp_list = []
            temp_list.append(i)                 # Appends ID
            temp_list.append(link.title)        # Appends Title
            temp_list.append(link.permalink)    # Appends Permalink
            temp_list.append(link.url)          # Appends URL
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


def read_conf():
    '''
    Get creds from conf file
    '''
    
    conf_list = []
    try:
        with open('redditpy.conf') as open_conf:
            # Creates a list of creds from conf file
            for i in open_conf:
                settings_list = i.strip().split('=')
                conf_list.append(settings_list[1])
    except IOError:    # redditpy.conf file not found
        print('Error: redditpy.conf not found')
        raise SystemExit()
    return conf_list


def login(reddit_user_agent, reddit_client_id, reddit_client_secret, reddit_username, reddit_password):
    '''
    Logs into account
    '''
    
    # Try to login or sleep/wait until logged in, or exit if user/pass wrong
    NotLoggedIn = True
    while NotLoggedIn:
        print("Logging In")
        try:
            reddit = praw.Reddit(
                user_agent=reddit_user_agent,
                client_id=reddit_client_id,
                client_secret=reddit_client_secret,
                username=reddit_username,
                password=reddit_password)
            print("Logged In")
            NotLoggedIn = False
        # TODO: Fix error handling
        except praw.errors.InvalidUserPass:
            print("Wrong username or password")
            raise SystemExit()
        except Exception as err:
            print(err)
    return reddit


def parse_saves(args_search, r):
    '''
    Creates list from saved
    list that matched a string
    '''
    
    if args_search != None:
        hit_list = []                       # List for match search strings
        for i in args_search:               # Loops through arguments for strings to match on
            for j in r.saved_list:          # Loops through saved list
                if i in j[1]:               # If string matches in title of saved list
                    hit_list.append(j)      # Append to hit_list
        write_html(hit_list)


def write_html(search_list):
    '''
    Creates html file for viewing
    '''
    
    try:
        with open('redditpy.html', 'w') as open_html:
            for i in search_list:
                open_html.write(str(i[0]) + ": <a href=https://www.reddit.com/" + i[2] + ">" +  i[1] + "</a> --- <a href=" + i[3] + ">Source</a><br />\n")
    except IOError:
        print('Error: Could not write to file')
        raise SystemExit()


def thread_loop(args_search, r):
    '''
    Creates threads to indicate the
    process is still parsing data
    '''
    
    t2 = threading.Thread(target=parse_saves, args=(args_search, r), name='t2')
    t2.start()
    while True:
        print('Parsing Data -', end='\r', flush=True)
        time.sleep(1)
        print('Parsing Data \\', end='\r', flush=True)
        time.sleep(1)
        print('Parsing Data |', end='\r', flush=True)
        time.sleep(1)
        print('Parsing Data /', end='\r', flush=True)
        time.sleep(1)
        if not t2.isAlive():
            print("Search Complete")
            break


def main():
    '''
    Starts main program
    '''
    
    parser = argparse.ArgumentParser(description='Finds information about Reddit user\'s account')
    parser.add_argument('-s', '--search', dest='search', help='Search for keyword in title', required=False, nargs='*', type=str)
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
    
    # Creates RedditPy object with argparse number of saved links to look through
    r = RedditPy(args.number)
    
    # Multithreading
    t1 = threading.Thread(target=thread_loop, args=(args.search, r), name='t1')
    
    t1.start()
    t1.join()


if __name__ == '__main__':
    main()
