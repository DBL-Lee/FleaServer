from celery import task
from post_office import mail
from models import EmailCode

@task()
def sendEmail():
    mail.send_queued()    

@task()
def deleteRow(pk):
    EmailCode.objects.get(pk=pk).delete()    
