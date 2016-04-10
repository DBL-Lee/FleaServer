from celery import task
from push_notifications.models import APNSDevice as Device
import requests
import json
from models import EaseToken
from calendar import timegm
from datetime import datetime,timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

EaseURL = "https://a1.easemob.com/fleamarket/fleamarket/"
Ease_id = "YXA62oYmkO_8EeWsf_N-l809Sg"
Ease_secret = "YXA6HFdIQSAr8uNulB1FzlYFeJYksfg"

@task()
def sendMessage(user,message,sender):
    devices = Device.objects.filter(user=user)
    devices.send_message(sender+":"+message)

@task()
def obtainrefreshToken():
    print "startToken"
    token = EaseToken.objects.first()
    if token is not None:
        if timezone.now()<token.expires_in:
            print "not expired"
            return

    data = {'grant_type':'client_credentials','client_id':Ease_id,'client_secret':Ease_secret}
    url = EaseURL+"token"
    r = requests.post(url,json=data)
    if r.status_code==requests.codes.ok:
        response = r.json()
        token = EaseToken.objects.first()
        if token is not None:
            print "needs refresh"
            token.token = response["access_token"]
            token.expires_in = timegm(datetime.utcnow().utctimetuple()) + response["expires_in"]
            token.application = response["application"]
            token.save()
        else:
            print "needs a new one"
            token = response["access_token"]
            expire = timezone.now()+timedelta(seconds=response["expires_in"])
            application = response["application"]
            EaseToken.objects.create(token=token,expires_in=expire,application=application)

    else:
       #obtain fail
       pass

@task()
def createEMaccount(email,username,password,nickname):
    obtainrefreshToken()
    url = EaseURL+"users"
    token = "Bearer "+EaseToken.objects.first().token
    header = {"Content-Type":"application/json","Authorization":token}
    data = {"username":username,"password":password,"nickname":nickname}
    r = requests.post(url,headers=header,json=data)
    print r.json()
    if r.status_code==requests.codes.ok:
         User = get_user_model()
         user = User.objects.filter(email=email).first()
         user.EMUser = username
         user.EMPass = password
         user.save()
    else:
        print r.text
