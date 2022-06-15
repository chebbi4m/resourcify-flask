import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
import yaml


config = yaml.safe_load(open(r'resourcify\database.yaml'))
client = MongoClient(config['uri'])
db = client['Resourcify']

comidocsite = "https://comidoc.net/coupons?page=1"
result = requests.get(comidocsite)
src = result.content

soup = BeautifulSoup(src, 'lxml')
db['coupons'].delete_many( { } )

maxPages = soup.find("div",class_="hidden w-32 justify-center rounded bg-th-background-medium p-4 py-2 font-medium text-th-accent-medium sm:flex")
maxPages=maxPages.text
for i in maxPages.split(" "):
    num=i
print(num)
final_data=[]

for i in range (int(num)+1)  :

    print(i)
    comidocsite = "https://comidoc.net/coupons?page="+ str(i)
    print(comidocsite +"======================")
    result2 = requests.get(comidocsite)
    src2 = result2.content
    soup2 = BeautifulSoup(src2, 'lxml')

    page_data= []
    for i in soup2.find_all("div",itemtype="http://schema.org/Course"):

        temp=[i.find_all('a',href=True)[2]]

        for j in temp:
            link=j.get('href')
            link="https://comidoc.net"+link
            print(link)


            result3 = requests.get(link)
            src3 = result3.content
            soup3 = BeautifulSoup(src3,'lxml') 


            getCoupon = soup3.find_all('td',string = "working")                         ##getting the coupon
            getName = soup3.find('h1',class_ = "text-4xl font-bold")                    ##getting the name
            getDescription = soup3.find('p',class_="pt-4 text-xl font-semibold sm:pt-2")##getting the description
            getPicture = soup3.find("video")                                            ##getting the picture
            getPrice = soup3.find("div",string="regular price")                         ##getting the price
            getCreatorName = soup3.find('a',class_="hover:underline")                   ##getting the creator name
            getId = soup3.find("div",string="udemy ID").parent
            
            for i in getId:
                udemyId = i.text
                break

            for i in getCoupon:
                coupons = i.parent
                row_text = [x.text for x in coupons.find_all('td')]
                coupons=row_text[2]
                couponType = row_text[3]

            for i in getName :
                name=i.text

            for i in getDescription:
                description=i.text

            if getPicture ==None:
                getPicture = soup.find('img',itemprop="thumbnail")   
                picture = getPicture['src']
            else:
                picture = getPicture["poster"]
                    
            for i in getPrice:
                temp = i.parent.parent
                row_text = [x.text for x in temp.find_all('div')]
                price = row_text[0]
                
            for i in getCreatorName:
                creatorName = i.text

            link = link . replace("https://comidoc.net/udemy/" , "https://www.udemy.com/course/")
                

            couponDict = {
                    'name' : name,
                    'description' : description,
                    'creatorName' : creatorName,
                    'picture' : picture,
                    'price' : price,
                    'couponType' : couponType,
                    'coupon' : coupons,
                    'link' : link,
                    'udemyId' : udemyId
            }
                

            db['coupons'].insert_one(couponDict)

        