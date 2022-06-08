import pyttsx3
import json

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
fileObject = open("quotesList.json", "r")
jsonContent = fileObject.read()
quotesList = json.loads(jsonContent)
# Pick a voice
enVoices = []
for x in voices:
    lang = x.languages[0]
    if x.name == "Kate":
        engine.setProperty("voice", x.id)

doneArray = []
# Main function
def convert(x):
    # name formating
    texts = x['quoteText'] + " " + x['quoteAuthor']
    name = ' '.join(x['quoteText'].split()[:8]) + "... - " + str(x['quoteAuthor'])
    mp3FileName = name + ".mp3"
    path = "mp3/" + mp3FileName
    print(mp3FileName)
    # Save
    engine.save_to_file(texts, path)
    # Write to quoteList
    x['name'] = name
    x['path'] = path
    doneArray.append(x)
    engine.startLoop()
    engine.stop()

# Done 365
for x in quotesList[:10]:
    convert(x)


# Write quotes form quotesListMP3.json
open('quotesListMP3.json', 'w').close()
with open('quotesListMP3.json', 'w') as f:
    json.dump(doneArray, f)
