from flask import Flask ,request
from flask_restful import Resource, Api
import requests
from requests.auth import HTTPBasicAuth
from flask_cors import CORS
from bs4 import BeautifulSoup




app = Flask(__name__)
api = Api(app)
CORS (app)

@app.route('/Courses',methods=['GET'])
def getCourses():

    args = request.args
    price = args.get('price', default="",type=str)
    category = args.get('category', default="",type=str)
    search = args.get('search', default="",type=str)
    language = args.get('language', default="",type=str)
    page_size = args.get('page_size', default="12",type=str)



    link='https://www.udemy.com/api-2.0/courses/'
    new_link = link+"?category="+category+"&price="+price+"&search="+search+"&language="+language + "&page_size=" + page_size

    print(new_link)
    response = requests.get(new_link,auth = HTTPBasicAuth('DmcabxNiiVj5slAK8ycd4F7Te7jySRezaZYfr4RS', 'pDdWt1Yw0bno9vMslAIAjelMIC95QuTHG3LBjB7rDUpMlpV2fkNpnQnD3MBR8QMoeAos0lzI06HSqz4lHDXflQQrYQbQdyiWJNVxqK0hjH8BQPwxYMl9BjixJTSaoTOa'))

    final_data=[]
    data = response.json()
    for i in data['results']:
        title = (i['title'])
        url = ("https://www.udemy.com" + i['url'])
        image = (i['image_480x270'])
        price = (i['price'])
        id = str((i['id']))

        json_data = {
        'name': title,
        'link': url,
        'picture' : image,
        'price' : price,
        'id' : id,
        }
        final_data.append(json_data)

    return {'data': final_data},200


@app.route('/Coupons',methods=['GET'])
def checkForCoupon():
    args = request.args
    url = args.get('url',default='',type=str)
    comidocsite = url.replace("https://www.udemy.com/course","https://comidoc.net/udemy")    ### provided by the angular from the specific couyrse
    print(comidocsite)
    result = requests.get(comidocsite)

    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    td_working = soup.find_all('td',string = "working")
    for i in td_working:
        coupons = i.parent
        print(coupons)
        row_text = [x.text for x in coupons.find_all('td')]
        coupons=row_text[2]
        if i == "":
            coupons = "no coupon found"
        else:
            coupons = coupons
       
        final_data = {
            'url' : url,
            'coupon' : coupons
        }
    return {'data': final_data},200




if __name__ == '__main__':
    app.run(debug=True)  # run our Flask app