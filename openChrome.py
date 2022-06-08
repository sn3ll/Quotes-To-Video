import json
from selenium import webdriver
with open('YouTubeUploader/cookies.json', 'r', newline='') as inputdata:
    cookies = json.load(inputdata)
curcookie = cookies[0]
print(curcookie)
driver = webdriver.Chrome()
driver.get("https://www.youtube.com")
driver.add_cookie(curcookie)
