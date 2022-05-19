from operator import index
from textwrap import indent
import time
from click import style
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
import yaml
from selenium import webdriver


config = yaml.safe_load(open('database.yaml'))
client = MongoClient(config['uri'])
db = client['Resourcify']

print("insert book link")
bookLink = input()

result = requests.get(bookLink)
src = result.content
soup = BeautifulSoup(src, 'lxml')
bookName = soup.find("h1",class_="ebook-title")
name = bookName.text
bookPicture = soup.find("img",class_="ebook-img")
picture = bookPicture['src']
bookInfo = soup.find_all("span",class_="info-green")
bookPage = bookInfo[0].text
bookRelease = bookInfo[1].text
bookSize = bookInfo[2].text

downloadPage = soup.find('a',class_="btn btn-primary btn-responsive")['href']

soup2 = BeautifulSoup(src, 'lxml')
downloadLink = soup2.find("a",class_="btn btn-primary btn-user")
print(downloadLink)