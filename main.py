import unsplash
import dril
from PIL import Image, ImageDraw, ImageFont

#Pick a new random image and load it
unsplash.getImage()
image = Image.open('data/background.jpg')

#Build the file and get a random quote
d = dril.Dril()
d.build() 
quote = d.quote()
print('"' + quote[1] + '" - @dril')

#Resize and crop the image?
p = 800/image.width
image = image.resize([int(image.width*p), int(image.height*p)])

#Testing with default font
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

draw.text((10, 10), quote[1], font=font)
image.show()

#Save image
image.save('background.jpg', "JPEG")