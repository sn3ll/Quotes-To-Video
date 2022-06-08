from multiprocessing import Pool
import json
from moviepy.editor import *
from os import walk
import random

fileObject = open("json/quotesListMP3.json", "r")
jsonContent = fileObject.read()
quotesList = json.loads(jsonContent)

print(len(quotesList))

filenames = next(walk('src/bg'), (None, None, []))[2]  # [] if no file
print(filenames)


def worker(x):
    print(x)
    # Import the audio(Insert to location of your audio instead of audioClip.mp3)
    audioPath = x['path']
    voiceAudio = AudioFileClip(audioPath)
    fullDuration = voiceAudio.duration + 3
    backgroundAudio = AudioFileClip("src/music.mp3").volumex(0.2)
    new_audioclip = CompositeAudioClip([voiceAudio.set_start(0.2), backgroundAudio])
    audio = new_audioclip.set_duration(fullDuration)
    # Import the Image and set its duration same as the audio (Insert the location of your photo instead of photo.jpg)
    randint = random.randint(0, len(filenames))
    print(randint)
    clip = ImageClip('src/bg/' + filenames[randint]).set_duration(fullDuration)
    # Set the audio of the clip
    clip = clip.set_audio(audio)
    # Text
    text = TextClip(txt=x['quoteText'] + "\n\n -" + x['quoteAuthor'],
                    size=[880, 1920],
                    fontsize=80,
                    color="black",
                    method='caption',
                    align='center'
                    )

    text = text.set_duration(audio.duration - 0.2).set_position((100, -100))

    # Merge video
    clip = CompositeVideoClip([clip, text.set_start(0.2)])

    # Export the clip
    exportpath = "mp4/" + x['name'] + ".mp4"
    clip.write_videofile(exportpath,
                         codec='libx264',
                         audio_codec='aac',
                         temp_audiofile='temp/' + x['name'] + '.m4a',
                         remove_temp=True,
                         fps=24,
                         )
    return


if __name__ == "__main__":
    pool = Pool(processes=10)  # start 4 worker processes
    for x in quotesList:
        pool.apply_async(worker, args=(x,))
    pool.close()
    pool.join()

