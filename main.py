#Main file
from csv import reader, writer, QUOTE_NONNUMERIC
import os, sys
import tweepy
import keys
import urllib3.contrib.pyopenssl

#Switch SSL to PyOpenSSL
urllib3.contrib.pyopenssl.inject_into_urllib3()

auth = tweepy.OAuthHandler(keys.keys['consumer_key'], keys.keys['consumer_secret'])
auth.set_access_token(keys.keys['access_token'], keys.keys['access_token_secret'])

#Connect to API
api = tweepy.API(auth)
total_rows = 0

def build_file(since):
    #Get recent tweets from dril and add to new file
    for status in tweepy.Cursor(api.user_timeline, 'dril', since_id=since).items():
        _process_status(status)
        total_rows += 1
        
    #Put content of old file in new file
    #This is kind of messy uhhh
    try:
        #Open things for reading and writing
        readFile = open('data/dril.csv', 'rb')
        writeFile = open('data/new.csv', 'ab')
        
        read = reader(readFile)
        write = writer(writeFile, delimiter=',', quoting=QUOTE_NONNUMERIC) #Uhhhhmmmmmhmh mmmm
        
        for row in read:
            write.writerow([int(row[0]), row[1]])
            total_rows += 1
    except IOError:
        print('Failed to open file (1) [okay if this is the first time running]')
        
    #Rename the new file to be the old file
    os.rename('data/new.csv', 'data/dril.csv')

def _process_status(status):
    try:
        with open('data/new.csv', 'ab') as writeFile:
            write = writer(writeFile, delimiter=',', quoting=QUOTE_NONNUMERIC)
            
            #Check to make sure it has just text content
            bad = len(status.entities['urls']) > 0 or len(status.entities['user_mentions']) > 0 or 'media' in status.entities or 'extended_entities' in status.entities
            if not bad:
                write.writerow([status.id, status.text.encode('ascii', 'ignore')])
                
            writeFile.close()
    except IOError: 
        print('Failed to open file (2)')

def get_since_id():
    newest = None
    try:
        with open('data/dril.csv', 'rb') as readFile:
            read = reader(readFile, delimiter=',')
            firstRow = next(read)
            newest = firstRow[0]
            readFile.close()
    except IOError:
        #Return newest as None to grab everything (even though this really isn't ideal aaaaaaahhh)
        print('Failed to open file (3) [okay if this is the first time running]')
        
    return newest 
    
#Run it     
since = get_since_id()
build_file(since)
print(total_rows)