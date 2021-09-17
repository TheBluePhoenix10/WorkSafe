# Python code to illustrate Sending mail from 
# your Gmail account 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
import requests

def send_mail(mailID,name,SPO2,HR,body):
    print('enter')
    string = "The Worksafe software has detected high temperature of "+ str(name)+" with following parameter= SPO2:"+ str(SPO2) +" HR:" + str(int(HR)) +" Body-Temperature:" + str(body)
    try:
        dataP = {'email':str(mailID),'string':string}
        url = 'https://worksafe.herokuapp.com/sendMail'
        r = requests.post(url, data=dataP)
        
    except Exception as e:
        print(e)
        pass 