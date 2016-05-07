#!/usr/bin/env python

#Main file

import unsplash
import dril
from html import unescape
from re import findall, compile
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageStat
from random import randrange

#Function to format quotes
def format_quote(quote):
    pattern = compile('[.?,!"#()*]+')
    breaks = pattern.findall(quote)
    
    newSegment = ''
    segments = []
    important = ['"','*','(',')','[',']']
    
    for item in quote.split():
        
        if '"' in item or '*' in item or '(' in item or ')' in item:
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
            
        elif '.' in item or '!' in item or ',' in item or '?' in item or '\n' in item:
            newSegment += item
            segments.append(newSegment)
            newSegment = ''
        
        else:
            newSegment += item + ' '
            
        #Break up segments that are getting too long
        if len(newSegment) > 70 and '"' not in newSegment and '*' not in newSegment and '(' not in newSegment:
            end = newSegment.find(' ', round(len(newSegment)/2))
            segments.append(newSegment[0:end])
            newSegment = newSegment[end:]
    
    #Add whatever's left
    if len(newSegment) > 0:
        segments.append(newSegment)
    
    #Strip whitespace
    segments = unescape([s.strip(' ') for s in segments])
    
    return segments
    
#Calculate the average brightness of the image and reduce if it's not dark enough to see white text
def adjust_brightness(image):
    #Find brightness of image
    temp = image.convert('L')
    stat = ImageStat.Stat(temp)
    brightness = (stat.mean[0]/255)
    
    if brightness > 0.35:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.75)
    
    return image

#Now take the segments and organize them to be drawn on the image
def beautify_quote(segments):
    #Arrays of font pairings
    #Was going to include more but they all had problems :'(
    fontPairs = [
        ['Debby', 'DroidSerif-Italic'],
        ['Debby', 'DroidSerif-Regular'],
        #['Kankin', 'DroidSerif-Regular']
    ]
    
    #Pick the nice and regular font from the arrays
    fontPair = fontPairs[randrange(len(fontPairs))] 
    
    #=====================================================
    organized = []
    """
    count = 0
    for segment in segments:
        if ':' in segment: count+=1
    
    #If it's a conversation ==============================
    if count > 1:
        for segment in segments:
            temp = {'font': None, 'size': None, 'text': segment}
            temp['font'] = fontPair[1]
            temp['size'] = 25
            organized.append(temp)
 
    else:
    """
    for segment in segments:
        temp = {'font': None, 'size': None, 'text': segment}
        
        #If it's small or in quotes or a hashtag, give it a nice font
        if '#' in segment or '"' in segment: #or len(segment) < 15 
            temp['font'] = fontPair[0]
            temp['size'] = 45
        
        #Otherwise
        else:
            temp['font'] = fontPair[1]
            temp['size'] = 15
        
        organized.append(temp)   
      
    return organized

if __name__ == "__main__":
    #Pick a new random image and load it
    unsplash.getImage('data/dril.png')
    image = Image.open('data/dril.png')
    
    #Build the file and get a random quote
    d = dril.Dril()
    d.build() 
    quote = d.quote()[1]
    print('"' + quote + '" - @dril')
    
    #Resize image to have 800px width and adjust brightness
    p = 800/image.width
    image = image.resize([int(image.width*p), int(image.height*p)])
    image = adjust_brightness(image)
    
    draw = ImageDraw.Draw(image)
    
    #Break quote into segments so they look nice when they're printed
    segments = format_quote(quote)
    imageText = beautify_quote(segments) #{'width': image.width, 'height': image.height}
    
    #Calculate stuff for printing
    maxHeight = 0
    for i in imageText: maxHeight += i['size']
    baseHeight = image.height/3
    
    #Write everything to the image
    for segment in imageText:
        font = ImageFont.truetype(font='fonts/'+segment['font']+'.ttf', size=segment['size'])
        width,height = font.getsize(segment['text'])
        draw.text(((image.width-width)/2, baseHeight), segment['text'], font=font)
        baseHeight += height

    #Save image
    image.save('data/dril.png', "PNG")