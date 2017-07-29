# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 15:37:38 2016

@author: bibekbehera
"""

import feedparser
import time
from subprocess import check_output
import sys
from text_summarizer import main

feed_name = ['FP','DH','CNN']
url = ['http://www.firstpost.com/sports/feed',
       'http://www.deccanherald.com/rss/sports.rss',
       'http://www.ibnlive.com/xml/rss/sports.xml']

#feed_name = sys.argv[1]
#url = sys.argv[2]

db = ['feeds_FP.txt','feeds_CNN.txt','feeds_DH.txt']
limit = 12 * 3600 * 1000

#
# function to get the current time
#
current_time_millis = lambda: int(round(time.time() * 1000))
current_timestamp = current_time_millis()

def post_is_in_db(link,i):
    with open(db[i], 'r') as database:
        for line in database:
            if link in line:
                return True
    return False

# return true if the title is in the database with a timestamp > limit
def post_is_in_db_with_old_timestamp(link,i):
    with open(db[i], 'r') as database:
        for line in database:
            if link in line:
                ts_as_string = line.split('|', 1)[1]
                ts = long(ts_as_string)
                if current_timestamp - ts > limit:
                    return True
    return False

#
# get the feed data from the url
#
for i in range(0,len(feed_name)):
    feed = feedparser.parse(url[i])

    #
    # figure out which posts to print
    #
    posts_to_print = []
    posts_to_skip = []
    
    for post in feed.entries:
        # if post is already in the database, skip it
        # TODO check the time
        link = post.id
        if post_is_in_db_with_old_timestamp(link,i):
            posts_to_skip.append(link)
        else:
            posts_to_print.append(link)
        
    #
    # add all the posts we're going to print to the database with the current timestamp
    # (but only if they're not already in there)
    #
    f = open(db[i], 'a')
    for link in posts_to_print:
        if not post_is_in_db(link,i):
            f.write(link + "|" + str(current_timestamp) + "\n")
    f.close
        
    #
    # output all of the new posts
    #
    count = 1
    blockcount = 1
    for link in posts_to_print:
        if blockcount>4:
            break
        if count % 5 == 1:
            print("\n" + time.strftime("%a, %b %d %I:%M %p") + '  ((( ' + feed_name[i] + ' - ' + str(blockcount) + ' )))')
            print("-----------------------------------------\n")
            blockcount += 1
        #print(link + "\n")
        m = main(link)
        print blockcount
        m.call_summarizer()
        count += 1