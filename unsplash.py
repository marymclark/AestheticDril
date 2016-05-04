#Script to request image from Unsplash
#Help with this found here: http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests

import shutil
import requests

#Get the image from request
def getImage(path = 'data/background.jpg'):
    r = requests.get('https://source.unsplash.com/random', stream=True)
    #If successful, write the content from the request to the path
    if r.status_code == 200:
        with open(path, 'wb') as image:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, image)
    else:
        print('Request was unsuccessful - status code: ' + r.status_code)