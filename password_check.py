import bcrypt
import os
from datetime import date
from datetime import datetime as dt
import os
import pymongo
from getmac import get_mac_address as gma
import pickle
import re, uuid
import requests

def checkPassword(password):
    passwd=b'pyqt543'
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd, salt)
    
    password_bcrypt=bcrypt.hashpw(bytes(password, encoding='utf-8'),salt)
    if password_bcrypt==hashed:
        return 1
    else:
        return 0
    
def check_Password(password,userEmail):
    # mongodb://worksafe:<password>@cluster0-shard-00-00.cb0y2.mongodb.net:27017,cluster0-shard-00-01.cb0y2.mongodb.net:27017,cluster0-shard-00-02.cb0y2.mongodb.net:27017/<dbname>?ssl=true&replicaSet=atlas-evo15g-shard-0&authSource=admin&retryWrites=true&w=majority
    # mongodb+srv://worksafe:safe123@cluster0.cb0y2.mongodb.net/spo2?retryWrites=true&w=majority
    # "mongodb://admin-sachin:Sachin123@cluster0-shard-00-00.pf7ee.mongodb.net:27017,cluster0-shard-00-01.pf7ee.mongodb.net:27017,cluster0-shard-00-02.pf7ee.mongodb.net:27017/spo2?ssl=true&replicaSet=atlas-x3z4ou-shard-0&authSource=admin&retryWrites=true&w=majority"
    myclient = pymongo.MongoClient("mongodb://worksafe:safe123@cluster0-shard-00-00.cb0y2.mongodb.net:27017,cluster0-shard-00-01.cb0y2.mongodb.net:27017,cluster0-shard-00-02.cb0y2.mongodb.net:27017/spo2?ssl=true&replicaSet=atlas-evo15g-shard-0&authSource=admin&retryWrites=true&w=majority")
    mydb = myclient["spo2"]
    mycol = mydb["identities"]
    MAC = str(':'.join(re.findall('..', '%012x' % uuid.getnode())))
    # MAC = str(gma())
    dataFromServer=None
    query = {"MAC": MAC}
    try:
        search = mycol.find_one(query)
        activationFromServer = search["ActivationKey"]
        email = search["Email"]
        if userEmail != email:
            return [4,0]
        dateFromServer = search["updated_at"].date()
        
    except:
        return [3,0]
     
    print("found in mongoDB")
  
    try:
        x = requests.get('http://worldclockapi.com/api/json/est/now')
        x=x.json()['currentDateTime'] [:10]
        today =dt.strptime(x, '%Y-%m-%d')
        today = today.date()
        print(today)
        # print(dateFromServer.days)
        difftime =  abs(today-dateFromServer) 
        difftime = difftime.days
        print(difftime)
        difftime = 30 - difftime
        print(difftime)
        if difftime > 0:
            print(activationFromServer)
            if str(activationFromServer)==str(password):
                return [1,difftime]
            else:
                return [0,difftime]
        else:
            return [2,0]
    except Exception as e:
        print(e)
        return [2,0]


