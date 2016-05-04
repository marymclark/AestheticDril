#Script to build a file of dril's tweets
#Also gets a random dril quote

from csv import reader, writer, QUOTE_NONNUMERIC
from random import randrange
import os, sys
import tweepy
import keys
#import urllib3.contrib.pyopenssl

#Switch SSL to PyOpenSSL (IN PYTHON 2 switched to python 3 bc it's just better)
#urllib3.contrib.pyopenssl.inject_into_urllib3()

auth = tweepy.OAuthHandler(keys.keys['consumer_key'], keys.keys['consumer_secret'])
auth.set_access_token(keys.keys['access_token'], keys.keys['access_token_secret'])

#Connect to API
api = tweepy.API(auth)

class Dril:
    def __init__(self):
        self.since = None
        self.total_rows = 0
    
    def _build_file(self):
        self.total_rows = 0 
        
        #Get recent tweets from dril and add to new file
        for status in tweepy.Cursor(api.user_timeline, 'dril', since_id=self.since).items():
            self.total_rows += self._process_status(status)
            
        #Put content of old file in new file
        #This is kind of messy uhhh
        try:
            #Open things for reading and writing
            readFile = open('data/dril.csv', 'rt', encoding='utf-8')
            writeFile = open('data/new.csv', 'at', encoding='utf-8')
            
            read = reader(readFile)
            write = writer(writeFile, delimiter=',', quoting=QUOTE_NONNUMERIC) #Uhhhhmmmmmhmh mmmm
            
            for row in read:
                write.writerow([int(row[0]), row[1]])
                self.total_rows += 1
        except IOError:
            print('Failed to open file (1) [okay if this is the first time running]')
            
        #Rename the new file to be the old file
        os.rename('data/new.csv', 'data/dril.csv')
    
    def _process_status(self, status):
        try:
            with open('data/new.csv', 'at', encoding='utf-8') as writeFile:
                write = writer(writeFile, delimiter=',', quoting=QUOTE_NONNUMERIC)
                
                #Check to make sure it has just text content
                bad = len(status.entities['urls']) > 0 or len(status.entities['user_mentions']) > 0 or 'media' in status.entities or 'extended_entities' in status.entities
                if not bad:
                    write.writerow([status.id, status.text]) #.encode('ascii', 'ignore') PYTHON 2
                else:
                    return 0
                    
                writeFile.close()
        except IOError: 
            print('Failed to open file (2)')
            
        return 1
    
    def _get_since_id(self):
        newest = None
        try:
            with open('data/dril.csv', 'rt', encoding='utf-8') as readFile:
                read = reader(readFile, delimiter=',')
                firstRow = next(read)
                newest = firstRow[0]
                readFile.close()
        except IOError:
            #Return newest as None to grab everything (even though this really isn't ideal aaaaaaahhh)
            print('Failed to open file (3) [okay if this is the first time running]')
            
        return newest 
        
    #Builds the file
    def build(self):
        self.since = self._get_since_id()
        #Make sure to build the file after not having made any requests for a while. Otherwise,
        #a "too many requests" error may occur.
        self._build_file()
    
    #Pick a random dril quote
    def quote(self):
        index = randrange(self.total_rows)
        line_indexed = None
            
        try:
            with open('data/dril.csv', 'rt', encoding='utf-8') as readFile:
                read = reader(readFile, delimiter=',')
                for i in range(0, index-1):
                    next(read)
                    i+=1
                line_indexed = next(read)
                
                readFile.close()
        except IOError:
            print('Failed to open file')
            
        return line_indexed