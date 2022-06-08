import os
import json

# Read quotes form quotesList.json
fileObject = open("json/quotesListMP3.json", "r")
jsonContent = fileObject.read()
quotesList = json.loads(jsonContent)


def upload(x):
    if x['quoteAuthor'] == "":
        name = x['quoteText']
    else:
        name = ' '.join(x['quoteText'].split()[:8]) + " = " + x['quoteAuthor']
    mp4FileName = x['pathMP4']
    script = "/Users/sn3ll/Documents/Quotes/YouTubeUploader/main.py"
    os.system("poetry run python3 " + script + " /Users/sn3ll/Documents/Quotes/" + mp4FileName + " -l YouTubeUploader/cookies.json -t '" + name + "' -d '" + x['quoteText'] + " " + x['quoteAuthor'] + "'" + " -T '" + " /Users/sn3ll/Documents/Quotes/" + x['thumb'] + "' --browser chrome")


for x in quotesList[321:340]:
    upload(x)
