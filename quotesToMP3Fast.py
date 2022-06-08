import pyttsx3
import json
from multiprocessing import Process, Queue, Pool, Manager
from os import walk

# initialize Text-to-speech engine
engine = pyttsx3.init()


# Function to end the text to speech engine at the end of each loop
def onEnd(name, completed):
    print('finished')
    engine.endLoop()


# get details of all voices available
voices = engine.getProperty("voices")
# Slow the rate from the default 200
engine.setProperty("rate", 170)
# Connect onEnd Function to engine
engine.connect('finished-utterance', onEnd)
# convert this text to speech
text = "A positive attitude can really make dreams come true - it did for me. David Bailey"
# Read quotes form quotesList.json
fileObject = open("json/quotesList.json", "r")
jsonContent = fileObject.read()
quotesList = json.loads(jsonContent)
# Pick a voice
enVoices = []
for x in voices:
    lang = x.languages[0]
    if x.name == "Kate":
        engine.setProperty("voice", x.id)


# Main function
def convert(x, q):
    # name formating
    texts = x['quoteText'] + " " + x['quoteAuthor']
    name = '-'.join(x['quoteText'].split()[:8]) + "-=-" + '-'.join(x['quoteAuthor'].split())
    mp3FileName = name + ".mp3"
    pathMP4 = "mp4/" + name + ".mp4"
    path = "mp3/" + mp3FileName
    print(mp3FileName)
    # Save
    engine.save_to_file(texts, path)
    # Write to quoteList
    x['name'] = name
    x['path'] = path
    x['pathMP4'] = pathMP4
    print(x)
    engine.startLoop()
    engine.stop()
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


if __name__ == "__main__":
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
        job = pool.apply_async(convert, args=(x, q))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    for job in jobs:
        job.get()

    # now we are done, kill the listener
    q.put('kill')
    pool.close()
    pool.join()


