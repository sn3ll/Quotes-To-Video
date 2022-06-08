import numpy as np
import json
from multiprocessing import Pool
from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects

# WE CREATE THE TEXT THAT IS GOING TO MOVE, WE CENTER IT.

fileObject = open("quotesListMP3.json", "r")
jsonContent = fileObject.read()
quotesList = json.loads(jsonContent)

print(len(quotesList))

# THE NEXT FOUR FUNCTIONS DEFINE FOUR WAYS OF MOVING THE LETTERS


# helper function
rotMatrix = lambda a: np.array([[np.cos(a), np.sin(a)],
                                [-np.sin(a), np.cos(a)]])


def vortex(screenpos, i, nletters):
    d = lambda t: 1.0 / (0.3 + t ** 8)  # damping
    a = i * np.pi / nletters  # angle of the movement
    v = rotMatrix(a).dot([-1, 0])
    if i % 2: v[1] = -v[1]
    return lambda t: screenpos + 400 * d(t) * rotMatrix(0.5 * d(t) * a).dot(v)


def cascade(screenpos, i, nletters):
    v = np.array([0, -1])
    d = lambda t: 1 if t < 0 else abs(np.sinc(t) / (1 + t ** 4))
    return lambda t: screenpos + v * 400 * d(t - 0.15 * i)


def arrive(screenpos, i, nletters):
    v = np.array([-1, 0])
    d = lambda t: max(0, 3 - 3 * t)
    return lambda t: screenpos - 400 * v * d(t - 0.2 * i)


def vortexout(screenpos, i, nletters):
    d = lambda t: max(0, t)  # damping
    a = i * np.pi / nletters  # angle of the movement
    v = rotMatrix(a).dot([-1, 0])
    if i % 2: v[1] = -v[1]
    return lambda t: screenpos + 400 * d(t - 0.1 * i) * rotMatrix(-0.2 * d(t) * a).dot(v)

# WE ANIMATE THE LETTERS

def moveLetters(letters, funcpos):
    return [letter.set_pos(funcpos(letter.screenpos, i, len(letters)))
            for i, letter in enumerate(letters)]
# WE USE THE PLUGIN findObjects TO LOCATE AND SEPARATE EACH LETTER

def worker(x):
    screensize = (1080, 1920)

    imgtext = 'lolimakiller'  #x['quoteText'] + "\n\n -" + x['quoteAuthor']

    print(imgtext)

    txtClip = TextClip(txt=imgtext, color='white', font="Amiri-Bold", method='caption',
                       fontsize=80)
    cvc = CompositeVideoClip([txtClip.set_pos('center')],
                             size=screensize)

    letters = findObjects(cvc)  # a list of ImageClips

    print(letters)

    clips = [CompositeVideoClip(moveLetters(letters, funcpos),
                                size=screensize).subclip(0, 5)
             for funcpos in [vortex, cascade, arrive, vortexout]]
    print(clips)

    # WE CONCATENATE EVERYTHING AND WRITE TO A FILE

    final_clip = concatenate_videoclips(clips)

    final_clip.write_videofile('coolTextEffects.mp4', fps=25, codec='mpeg4')


if __name__ == "__main__":
    pool = Pool(processes=1)  # start 4 worker processes
    for x in quotesList[:1]:
        pool.apply_async(worker, args=(x,))
    pool.close()
    pool.join()


