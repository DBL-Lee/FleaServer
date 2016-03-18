#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rest_framework import status,filters, mixins,generics,pagination,permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from product.models import Product,PrimaryCategory,Version,EmailCode,MyUser
from product.serializers import ProductSerializer,PriCatSerializer,UserSerializer
from django.http import HttpResponse
import django_filters
from django.contrib.auth import get_user_model

from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import string
import random
from post_office import mail
from django.core.mail import send_mail
from product.tasks import sendEmail,deleteRow
def verifycodegenerator(size=5,chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class EmailUser(APIView):
    def post(self,request, *args, **kwargs):
        email = request.data.get("email",None)
        if email is not None:
            code = verifycodegenerator()
            store = EmailCode.objects.create(code=code)
            mail.send([email],subject="FleaMddarket验证码",priority="medium",message=code)
            sendEmail.delay()
            deleteRow.apply_async((store.pk,), countdown=600)

            return Response(data=store.pk,status=200)
        return Response(status=400)

def upVersion():
    version = Version.objects.get(pk=1)
    version.version += 1
    version.save()

class VersionedListCreateAPIView(generics.ListCreateAPIView):
    def perform_create(self, serializer):
        super(VersionedListCreateAPIView,self).perform_create(serializer)
        upVersion()


class VersionedRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    def perform_update(self, serializer):
        super(VersionedRetrieveUpdateDestroyAPIView,self).perform_update(serializer)
        upVersion()

    def perform_destroy(self, instance):
        super(VersionedRetrieveUpdateDestroyAPIView,self).perform_destroy(instance)
        upVersion()

def currentVersion(request):
    return HttpResponse(str(Version.objects.get(pk=1).version))


class ProductFilter(filters.FilterSet):
    min_price = django_filters.NumberFilter(name="price", lookup_type='gte')
    max_price = django_filters.NumberFilter(name="price", lookup_type='lte')
    primarycategory = django_filters.NumberFilter(name="category__primaryCategory__pk")
    secondarycategory = django_filters.NumberFilter(name="category__pk")
    class Meta:
        model = Product
        fields = ['min_price','max_price','primarycategory','secondarycategory','brandNew','bargain','exchange']

class ProductList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = ProductSerializer
    filter_class = ProductFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):  
        sortType = self.request.query_params.get('sorttype',None)
        queryset = Product.objects.all()
        titleq = self.request.query_params.get('title',None)
        if titleq is not None:
            queryset = queryset.filter(title__icontains=titleq)
        
        latitude = self.request.query_params.get('latitude',None)
        longitude = self.request.query_params.get('longitude',None)
        distance = self.request.query_params.get('distance',1000)
        if latitude is not None:
            queryset = queryset.nearby(float(latitude),float(longitude),float(distance))
        if sortType is not None:
            if sortType=="distance":
                #do nothing already sorted by distance
                print "distance"
            elif sortType=="price":
                queryset = queryset.orderByPriceAscending()
            elif sortType=="-price":
                queryset = queryset.orderByPriceDescending()
            elif sortType=="posttime":
                queryset = queryset.orderByPostTime()
            elif sortType=="default":
                queryset = queryset.orderByPostTime()
            else:
                queryset = Product.objects.all()

        return queryset

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryList(VersionedListCreateAPIView):
    queryset = PrimaryCategory.objects.all()
    serializer_class = PriCatSerializer
    pagination_class = None

class CategoryDetail(VersionedRetrieveUpdateDestroyAPIView): 
    queryset = PrimaryCategory.objects.all()
    serializer_class = PriCatSerializer

class UserRegister(generics.CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer

    def post(self,request,*args,**kwargs):
        #verify email
        try:
            store = EmailCode.objects.get(pk=request.data["id"])
            if store.code!=request.data["code"]:
                #wrong verification code
                return Response({"error":"1"},status=400)
        except EmailCode.DoesNotExist:
            #code expired
            return Response({"error":"2"},status=400)
        
        email = request.data["email"]
        #check email not exist
        if MyUser.objects.filter(email=email).exists():
            #duplicate email
            return Response({"error":"3"},status=400)

        #check nickname not exist
        if MyUser.objects.filter(nickname=request.data["nickname"]).exists():
            #duplicate nickname
            return Response({"error":"4"},status=400)

        return super(UserRegister,self).post(request,args,kwargs)
