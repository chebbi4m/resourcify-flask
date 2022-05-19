from operator import index
from textwrap import indent
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
import yaml

config = yaml.safe_load(open('database.yaml'))
client = MongoClient(config['uri'])
db = client['Resourcify']

bookSite = "https://www.pdfdrive.com/category/"
pageCounter = 0
for i in range(250):
    pageCounter = pageCounter + 1
    result = requests.get(bookSite + str(pageCounter))
    src = result.content

    soup = BeautifulSoup(src, 'lxml')

    getCategoryName = soup.find("div",class_="collection-title").text
    print(str(pageCounter) + "***" +getCategoryName )

