from django.shortcuts import render
from rest_framework import status,filters, mixins,generics,pagination,permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_jwt import views as jwt_view
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from chat.tasks import sendMessage
from collections import OrderedDict
from push_notifications.models import APNSDevice


class SendMessageToUser(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def post(self,request,*args,**kwargs):
        userid = request.data["targetuser"]
        targetUser = get_user_model().objects.get(pk=userid)
        message = request.data["message"]
        sender = request.user
        sendMessage.delay(targetUser,message,sender.nickname)
        return Response(status=200)

class PostAPNSDevice(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    
    def post(self,request,*args,**kwargs):
        token = request.data["APNSToken"]
        if APNSDevice.objects.all().filter(registration_id=token).exists():
            return self.update(request,*args,**kwargs)
        else:
            return self.create(request,*args,**kwargs)

    def create(self,request,*args,**kwargs):
        token = request.data["APNSToken"]
        device = APNSDevice.objects.create(registration_id=token)
        device.user = request.user
        device.save()
        return Response(status=201)

    def update(self,request,*args,**kwargs):
        token = request.data["APNSToken"]
        device = APNSDevice.objects.get(registration_id=token)
        device.user = request.user
        device.save()
        return Response(status=201)
# Create your views here.
