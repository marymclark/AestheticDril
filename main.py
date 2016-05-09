#!/usr/bin/env python

#Main file

import unsplash
import dril
import keys
from html import unescape
#from re import findall, compile
import logging
import tweepy
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageStat
from random import randrange

#Function to format quotes
def format_quote(quote):
    #pattern = compile('[.?,!"#()*]+')
    #breaks = pattern.findall(quote)
    
    newSegment = ''
    segments = []
    important = ['"','*','(',')','[',']']
    
    for item in quote.split():
        item = unescape(item)
        
        if '"' in item or '*' in item or '(' in item or ')' in item:
            """
            #Maybe add this?
            if len(item) <= 1:
                segments[len(segments-1)] += item
            """
                
            #Count occurrences in item
            count = 0
            for letter in item:
                if letter in important: count+=1
            
            #Add to segment if already inside a quote, then append and clear
            if '"' in newSegment or '*' in newSegment or '(' in newSegment:
                newSegment += item
                segments.append(newSegment)
                newSegment = ''
            #If symbol isn't already in the newSegment, and if it's in the item twice, append and clear new segment
            elif count > 1:
                segments.append(newSegment)
                segments.append(item)
                newSegment = ''
            #If not in a quote, append the string, clear, then start the quote
            else:
                if len(newSegment) > 0:
                    segments.append(newSegment)
                newSegment = ''
                newSegment += item + ' '
            
        elif '#' in item:
            #Append existing text, then hashtag, then clear string
            segments.append(newSegment)
            segments.append(item)
            newSegment = ''
            
        #Trying to figure out how to get the returns in the csv? :/
        elif '.' in item or '!' in item or ',' in item or '?' in item or '\n' in item or '\r' in item:
            if len(item) <= 1:
                newSegment += ' ' + item
            else:
                newSegment += item
                segments.append(newSegment)
                newSegment = ''
        
        else:
            newSegment += item + ' '
            
        #Break up segments that are getting too long
        if len(newSegment) > 70: #and '"' not in newSegment and '*' not in newSegment and '(' not in newSegment:
            end = newSegment.find(' ', round(len(newSegment)/2))
            segments.append(newSegment[0:end])
            newSegment = newSegment[end:]
    
    #Add whatever's left
    if len(newSegment) > 0:
        segments.append(newSegment)
    
    #Strip whitespace
    segments = [s.strip(' ') for s in segments]
    
    return segments
    
#Calculate the average brightness of the image and reduce if it's not dark enough to see white text
def adjust_brightness(image):
    #Find brightness of image
    temp = image.convert('L')
    stat = ImageStat.Stat(temp)
    brightness = (stat.mean[0]/255)
    
    #Think this makes more sense
    enhancer = ImageEnhance.Brightness(image)
    if brightness > 0.10:
        image = enhancer.enhance(1.10-brightness)
    """
    if brightness > 0.35:
        image = enhancer.enhance(0.75)
    elif brightness > 0.60:
        image = enhancer.enhance(0.50)
    """
    
    return image

#Now take the segments and organize them to be drawn on the image
def beautify_quote(segments):
    #Arrays of font pairings
    #Was going to include more but they all had problems :'(
    fontPairs = [
        ['Debby', 'DroidSerif-Italic'],
        ['Debby', 'DroidSerif-Regular'],
        ['Lovelo Line Light', 'sf-new-republic.sc'],
    ]
    
    #Pick the nice and regular font from the arrays
    fontPair = fontPairs[randrange(len(fontPairs))] 
    
    organized = []
    nothingFancy = True
    for segment in segments:
        if '#' in segment or '"' in segment:
            nothingFancy = False

    for segment in segments:
        temp = {'font': None, 'size': None, 'text': segment}
        
        #If it's small or in quotes or a hashtag, give it a nice font
        if '#' in segment or '"' in segment: #or len(segment) < 15 
            temp['font'] = fontPair[0]
            temp['size'] = 50
        #If nothing else is going to be in a nice font, put small text in a nice font...?
        elif nothingFancy and len(segment) <= 20:
            temp['font'] = fontPair[0]
            temp['size'] = 50
        #Otherwise
        else:
            temp['font'] = fontPair[1]
            temp['size'] = 20
        
        organized.append(temp)   
      
    return organized

def create_image(quote, path):
    #Pick a new random image and load it
    unsplash.getImage(path)
    image = Image.open(path)
    
    #Resize image to have 800px width and adjust brightness
    p = 800/image.width
    image = image.resize([int(image.width*p), int(image.height*p)])
    image = adjust_brightness(image)
    
    draw = ImageDraw.Draw(image)
    
    #Break quote into segments so they look nice when they're printed
    segments = format_quote(quote)
    imageText = beautify_quote(segments) #{'width': image.width, 'height': image.height}
    
    #Calculate stuff for printing
    tempHeight = 0
    for segment in imageText:
        font = ImageFont.truetype(font='fonts/'+segment['font']+'.ttf', size=segment['size'])
        height = font.getsize(segment['text'])[1]
        tempHeight += height
    baseHeight = (image.height - tempHeight)/2
    
    #Write everything to the image
    for segment in imageText:
        font = ImageFont.truetype(font='fonts/'+segment['font']+'.ttf', size=segment['size'])
        width,height = font.getsize(segment['text'])
        draw.text(((image.width-width)/2, baseHeight), segment['text'], font=font)
        baseHeight += height+2

    #Save image
    image.save('data/dril.png', "PNG")
    
if __name__ == "__main__":
    logging.basicConfig(filename='data/info.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('Began running script...')
    
    #Build the file and get a random quote
    d = dril.Dril()
    d.build() 
    quote = d.quote()[1]
    print('"' + quote + '" - @dril')
    
    #Create image
    create_image(quote, 'data/dril.png')

    #Authenticate
    auth = tweepy.OAuthHandler(keys.keys['consumer_key'], keys.keys['consumer_secret'])
    auth.set_access_token(keys.keys['access_token'], keys.keys['access_token_secret'])
    api = tweepy.API(auth)
    
    #Update
    try:
        #api.update_with_media('data/dril.png')
        logging.info('Updated successfully')
    except Exception:
        logging.info('Update failed: ' + str(Exception))