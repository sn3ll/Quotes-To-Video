from PIL import Image, ImageDraw, ImageFont
from os import walk
import random
import json
import textwrap
import string
from multiprocessing import Process, Queue, Pool, Manager

# create Image object
text1 = 'Create Feature Image'
text2 = 'With Python'
img_name = 'featured-image-creation-with-python.png'
color = 'grey'  # grey,light_blue,blue,orange,purple,yellow,green
font = 'Roboto-Bold.ttf'

# create the coloured overlays
colors = {
    'dark_blue': {'c': (27, 53, 81), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(255, 212, 55)'},
    'grey': {'c': (70, 86, 95), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(93,188,210)'},
    'light_blue': {'c': (93, 188, 210), 'p_font': 'rgb(27,53,81)', 's_font': 'rgb(255,255,255)'},
    'blue': {'c': (23, 114, 237), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(255, 255, 255)'},
    'orange': {'c': (242, 174, 100), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(0,0,0)'},
    'purple': {'c': (114, 88, 136), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(255, 212, 55)'},
    'red': {'c': (255, 0, 0), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(0,0,0)'},
    'yellow': {'c': (255, 255, 0), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(27,53,81)'},
    'yellow_green': {'c': (232, 240, 165), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(0,0,0)'},
    'green': {'c': (65, 162, 77), 'p_font': 'rgb(217, 210, 192)', 's_font': 'rgb(0, 0, 0)'}
}


def add_color(image, c, transparency):
    color = Image.new('RGB', image.size, c)
    mask = Image.new('RGBA', image.size, (0, 0, 0, transparency))
    return Image.composite(image, color, mask).convert('RGB')

def center_text(img, font, text1, text2, fill1, fill2):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    t1_width, t1_height = draw.textsize(text1, font)
    t2_width, t2_height = draw.textsize(text2, font)
    p1 = ((w - t1_width) / 2, h // 3)
    p2 = ((w - t2_width) / 2, h // 3 + h // 2.5)
    draw.text(p1, text1, fill=fill1, font=font)
    draw.text(p2, text2, fill=fill2, font=font)
    return img


def add_text(img, color, text1, text2, logo=False, font='Roboto-Bold.ttf', font_size=75):
    draw = ImageDraw.Draw(img)

    p_font = color['p_font']
    s_font = color['s_font']

    # starting position of the message
    img_w, img_h = img.size
    height = img_h // 3
    font = ImageFont.truetype(font, size=font_size)

    if logo == False:
        center_text(img, font, text1, text2, p_font, s_font)
    else:
        text1_offset = (img_w // 4, height)
        text2_offset = (img_w - 300)
        draw.text(text1_offset, text1, fill=p_font, font=font)
        draw.text(text2_offset, text2, fill=s_font, font=font)
    return img


def add_logo(background, foreground):
    bg_w, bg_h = background.size
    img_w, img_h = foreground.size
    img_offset = (20, (bg_h - img_h) // 2)
    background.paste(foreground, img_offset, foreground)
    return background


def write_image(background, color, text1, text2, foreground=''):
    background = add_color(background, color['c'], 50)
    if not foreground:
        add_text(background, color, text1, text2)
    else:
        add_text(background, color, text1, text2, logo=True)
        add_logo(background, foreground)
    return background


fileObject = open("json/quotesListMP3.json", "r")
jsonContent = fileObject.read()
quotesList = json.loads(jsonContent)

filenames = next(walk('src/thumb'), (None, None, []))[2]  # [] if no file


def thumbnailer(x, q):
    randint = random.randint(0, 10)
    backgroundtemp = Image.open("src/thumb/" + filenames[randint])
    background = backgroundtemp.resize((1920, 1080))
    print(background)

    caption = x['quoteText']

    wrapper = textwrap.TextWrapper(width=50)
    word_list = wrapper.wrap(text=caption)
    caption_new = ''
    for ii in word_list[:-1]:
        caption_new = caption_new + ii + '\n'
    caption_new += word_list[-1]

    # printing letters
    letters = string.ascii_letters
    hash = (''.join(random.choice(letters) for i in range(10)))

    thumbnailpath = "thumb/" + str(randint) + hash + ".png"
    thumbnail = write_image(background, colors[color], caption_new, x['quoteAuthor'])
    thumbnail.save(thumbnailpath)
    x['thumb'] = thumbnailpath
    q.put(x)
    return x


def listener(q):
    with open('json/quotesListMP3.json', 'r+') as file:
        data = json.load(file)
        while 1:
            m = q.get()
            if m == 'kill':
                break
            data.append(m)
            file.seek(0)
            json.dump(data, file)


if __name__ == '__main__':
    f = open('json/quotesListMP3.json', 'w')
    f.write("[]")
    f.close()

    # must use Manager queue here, or will not work
    manager = Manager()
    q = manager.Queue()
    pool = Pool(processes=10)

    # put listener to work first
    watcher = pool.apply_async(listener, (q,))

    # fire off workers
    jobs = []

    for x in quotesList:
        job = pool.apply_async(thumbnailer, args=(x, q))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    for job in jobs:
        job.get()

    # now we are done, kill the listener
    q.put('kill')
    pool.close()
    pool.join()

