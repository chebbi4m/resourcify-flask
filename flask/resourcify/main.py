import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import string
from flask import Flask ,request, jsonify
from flask_restful import Resource, Api
import requests
from requests.auth import HTTPBasicAuth
from flask_cors import CORS
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
import yaml


app = Flask(__name__)
api = Api(app)
config = yaml.safe_load(open('database.yaml'))
client = MongoClient(config['uri'])
db = client['Resourcify']
CORS (app)



def print_date_time():
    comidocsite = "https://comidoc.net/coupons?page=1"
    result = requests.get(comidocsite)
    src = result.content

    soup = BeautifulSoup(src, 'lxml')
    db['coupons'].delete_many( { } )

    maxPages = soup.find("div",class_="hidden w-32 justify-center rounded bg-th-background-medium p-4 py-2 font-medium text-th-accent-medium sm:flex")
    maxPages=maxPages.text
    for i in maxPages.split(" "):
        num=i

    for i in range (int(num)+1)  :

        comidocsite = "https://comidoc.net/coupons?page="+ str(i)
        result2 = requests.get(comidocsite)
        src2 = result2.content
        soup2 = BeautifulSoup(src2, 'lxml')

        for i in soup2.find_all("div",itemtype="http://schema.org/Course"):

            temp=[i.find_all('a',href=True)[2]]

            for j in temp:
                link=j.get('href')
                link="https://comidoc.net"+link


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
                

                couponDict = {
                    'name' : name,
                    'description' : description,
                    'creatorName' : creatorName,
                    'picture' : picture,
                    'price' : price,
                    'couponType' : couponType,
                    'coupon' : coupons,
                    'udemyId' : udemyId
                }
                    

                db['coupons'].insert_one(couponDict)

@app.route('/check',methods=['GET'])
def checkForCoupon():

######## Check For Coupon ########

    args = request.args
    url = args.get('url',default='',type=str)
    final_data = {}
    coupons = ''

    if url != '':
        comidocsite = url.replace("https://www.udemy.com/course","https://comidoc.net/udemy")    ### provided by the angular from the specific couyrse
        result = requests.get(comidocsite)
        src = result.content
        soup4 = BeautifulSoup(src, 'lxml')

        getCoupon = soup4.find_all('td',string = "working") ##getting the coupon
        getId = soup4.find("div",string="udemy ID").parent

        for i in getId:
            udemyId = i.text
            break

        for i in getCoupon:
            coupons = i.parent
            row_text = [x.text for x in coupons.find_all('td')]
            coupons=row_text[2]     

        final_data = {
            'coupons' : coupons,
            'udemyId' : udemyId,
        }
    return final_data,200

###### Get Multiple Coupons ######
@app.route('/Coupons',methods=['GET'])
def getCoupons():

    allData = db['coupons'].find()
    dataJson = []
    for data in allData:
        title = data['name']
        description = data['description']
        creatorName = data['creatorName']
        image = data['picture']
        price = data['price']
        coupon = data['coupon']
        couponType = data['couponType']
        udemyId = data['udemyId']
        dataDict = {
                    "name": title,
                    "description": description,
                    "creator":creatorName,
                    "picture": image,
                    "price": price,
                    "coupon": coupon,
                    "couponType":couponType,
                    "udemyId": udemyId
            }
        dataJson.append(dataDict)
    return jsonify(dataJson) 

@app.route('/Coupons/100off',methods=['GET'])
def get100OffCoupons():

    allData = db['coupons'].find({"couponType": "100% OFF"})   
    dataJson = []
    for data in allData:
        title = data['name']
        description = data['description']
        creatorName = data['creatorName']
        image = data['picture']
        price = data['price']
        coupon = data['coupon']
        couponType = data['couponType']
        udemyId = data['udemyId']
        dataDict = {
                    "name": title,
                    "description": description,
                    "creator":creatorName,
                    "picture": image,
                    "price": price,
                    "coupon": coupon,
                    "couponType":couponType,
                    "udemyId": udemyId
            }
        dataJson.append(dataDict)
    return jsonify(dataJson)

@app.route('/Coupons/other',methods=['GET'])
def gettherCoupons():

    allData = db['coupons'].find({"couponType": {"$ne": "100% OFF"}})
    dataJson = []
    for data in allData:
        title = data['name']
        description = data['description']
        creatorName = data['creatorName']
        image = data['picture']
        price = data['price']
        coupon = data['coupon']
        couponType = data['couponType']
        udemyId = data['udemyId']
        dataDict = {
                    "name": title,
                    "description": description,
                    "creator":creatorName,
                    "picture": image,
                    "price": price,
                    "coupon": coupon,
                    "couponType":couponType,
                    "udemyId": udemyId
            }
        dataJson.append(dataDict)
    return jsonify(dataJson)


@app.route('/Course/<udemyId>',methods=['GET'])
def CourseById(udemyId:string):

    link='https://www.udemy.com/api-2.0/courses/'
    link = link + udemyId
    response = requests.get(link,auth = HTTPBasicAuth('DmcabxNiiVj5slAK8ycd4F7Te7jySRezaZYfr4RS', 'pDdWt1Yw0bno9vMslAIAjelMIC95QuTHG3LBjB7rDUpMlpV2fkNpnQnD3MBR8QMoeAos0lzI06HSqz4lHDXflQQrYQbQdyiWJNVxqK0hjH8BQPwxYMl9BjixJTSaoTOa'))
    data = response.json()
    courseLink = data['url']
    courseLink = "https://www.udemy.com" + courseLink
    title = data['title']
    image = data['image_480x270']
    price = data['price']
    json_data = {
        'name': title,
        'link': courseLink,
        'picture' : image,
        'price' : price,
        'id' : udemyId
    }

    return jsonify(json_data),200

@app.route('/Coupons/claim/<udemyId>',methods=['GET'])
def claimCourse(udemyId:string):
    
    args = request.args
    coupon = args.get('couponCode', default="",type=str)
    link='https://www.udemy.com/api-2.0/courses/'
    link = link + udemyId
    response = requests.get(link,auth = HTTPBasicAuth('DmcabxNiiVj5slAK8ycd4F7Te7jySRezaZYfr4RS', 'pDdWt1Yw0bno9vMslAIAjelMIC95QuTHG3LBjB7rDUpMlpV2fkNpnQnD3MBR8QMoeAos0lzI06HSqz4lHDXflQQrYQbQdyiWJNVxqK0hjH8BQPwxYMl9BjixJTSaoTOa'))
    data = response.json()
    courseLink = data['url']
    courseLink = "https://www.udemy.com" + courseLink + "?couponCode=" + coupon

    return jsonify(courseLink),200

@app.route('/Courses/Udemy',methods=['GET'])
def getCourses():

    args = request.args
    price = args.get('price', default="",type=str)
    category = args.get('category', default="",type=str)
    search = args.get('search', default="",type=str)
    language = args.get('language', default="",type=str)

    link='https://www.udemy.com/api-2.0/courses/'
    new_link = link+"?category="+category+"&price="+price+"&search="+search+"&language="+language + "&page_size=" + "200"

    response = requests.get(new_link,auth = HTTPBasicAuth('DmcabxNiiVj5slAK8ycd4F7Te7jySRezaZYfr4RS', 'pDdWt1Yw0bno9vMslAIAjelMIC95QuTHG3LBjB7rDUpMlpV2fkNpnQnD3MBR8QMoeAos0lzI06HSqz4lHDXflQQrYQbQdyiWJNVxqK0hjH8BQPwxYMl9BjixJTSaoTOa'))

    final_data=[]
    data = response.json()
    for i in data['results']:
        title = (i['title'])
        url = ("https://www.udemy.com" + i['url'])
        image = (i['image_480x270'])
        price = (i['price'])
        headline = (i['headline'])
        id = str((i['id']))
        for j in i['visible_instructors']:
            creator = (j['display_name'])

        json_data = {
        'name': title,
        'link': url,
        'picture' : image,
        'price' : price,
        'headline' : headline,
        'creator' : creator,
        'id' : id,
        }
        final_data.append(json_data)

    return {'data': final_data},200

@app.route('/Courses/add', methods=['POST'])
def addCourse():
    # POST a data to database
    if request.method == 'POST':
        body = request.json
        email = body['email']
        creator = body['creator']
        title = body['name']
        url = body['link']
        image = body['picture']
        price = body['price']
        id = body['id']

        db['MyCourses'].insert_one({
            "email": email,
            "name": title,
            "link": url,
            "picture": image,
            "price": price,
            "creator" : creator,
            "id": id,
        })
        return jsonify({
            'status': 'Data is posted to MongoDB!',
            'name' : title
        })
    
    
        # GET a specific data by id
    if request.method == 'GET':
        data = db['users'].find_one({'_id': ObjectId(id)})
        title = data['name']
        creator = body['creator']
        url = data['link']
        image = data['picture']
        price = data['price']
        id = data['id']
        dataDict = {
             "name": title,
                "link": url,
                "picture": image,
                "price": price,
                'creator' : creator,
                "id": id,
        }
        return jsonify(dataDict)
        

@app.route('/Courses/all/<Email>', methods=[ 'GET'])
def getAllCourses(Email:string):
    # GET all data from database
    if request.method == 'GET':
        allData = db['MyCourses'].find({'email' : Email})
        dataJson = []
        for data in allData:
            email = data['email']
            creator = data['creator']
            title = data['name']
            url = data['link']
            image = data['picture']
            price = data['price']
            id = data['id']
            dataDict = {
                "email" : email,
                "name": title,
                "link": url,
                "picture": image,
                "price": price,
                'creator' : creator,
                "id": id,
            }
            dataJson.append(dataDict)
    return jsonify(dataJson)

@app.route('/Courses/delete/<id>/<email>', methods=[ 'DELETE'])
def deleteCoursebyId(id:string,email:string):
    # DELETE a data
    if request.method == 'DELETE':

        myquery = {
            "id" : id,
            "email" : email
            } 

        db['MyCourses'].delete_one(myquery)
        return jsonify({'status': 'Data id: ' + id + ' is deleted!'})

        ##BOOKS##
@app.route('/Books/add', methods=['POST'])
def addBook():

    body = request.json
    bookName = body['name']
    bookPicture = body['picture']
    bookPages = body['pages']
    bookSize = body['size']
    bookDownload = body['link']


    db['Books'].insert_one({
        "name": bookName,
        "picture": bookPicture,
        "pages": bookPages,
        "size": bookSize,
        "download": bookDownload,
    })
    return jsonify({
            'status': 'Data is posted to MongoDB!',
            'name' : bookName
        })

@app.route('/Books/all', methods=[ 'GET'])
def getAllBooks():
    # GET all data from database
    if request.method == 'GET':
        allData = db['Books'].find()
        dataJson = []
        for data in allData:
            bookName = data['name']
            bookPicture = data['picture']
            bookPages = data['pages']
            bookSize = data['size']
            bookDownload = data['download']
            dataDict = {
                "name": bookName,
                "picture": bookPicture,
                "pages": bookPages,
                "size": bookSize,
                "download": bookDownload,
            }
            dataJson.append(dataDict)
        return jsonify(dataJson)


scheduler = BackgroundScheduler()
scheduler.add_job(func=print_date_time, trigger="interval", minutes=60)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True)  # run our Flask app