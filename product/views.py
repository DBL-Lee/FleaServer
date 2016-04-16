#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rest_framework import status,filters, mixins,generics,pagination,permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from product.models import Product,PrimaryCategory,Version,EmailCode,MyUser,OrderMembership
from product.serializers import ProductSerializer,PriCatSerializer,UserSerializer,OrderPeopleSerializer,OrderSerializer,AwaitingAcceptProductSerializer
from django.http import HttpResponse
import django_filters
from django.contrib.auth import get_user_model
from rest_framework_jwt import views as jwt_view
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import string
import random
from post_office import mail
from django.core.mail import send_mail
from product.tasks import sendEmail,deleteRow
from collections import OrderedDict
from push_notifications.models import APNSDevice
from chat.tasks import obtainrefreshToken,createEMaccount

class SelfOrderedProduct(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = OrderSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return self.request.user.getOrderedOrder()
   

class SelfPendingBuyProduct(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = ProductSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return self.request.user.getPendingBuyProduct()


class SelfPostedProduct(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = ProductSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return self.request.user.getPostedProduct()

class SelfAwaitingAcceptProduct(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = AwaitingAcceptProductSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return self.request.user.getAwaitingAcceptProduct()

class SelfAwaitingPeople(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = OrderPeopleSerializer
    
    def get_queryset(self):
        id = self.request.query_params["productid"]
        return self.request.user.getAwaitingAcceptOrder().filter(product__id=id)

class SelfSoldProduct(generics.ListAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = ProductSerializer

    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return self.request.user.getSoldProduct()

    
class SelfBoughtProduct(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = ProductSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return self.request.user.getBoughtProduct()

class UpdateUser(generics.UpdateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def post(self,request,*args,**kwwargs):
        avatar = request.data.get("avatar",None)
        if avatar is not None:
            request.user.avatar = avatar

        gender = request.data.get("gender",None)
        if gender is not None:
            request.user.gender = gender

        location = request.data.get("location",None)
        if location is not None:
            request.user.location = location

        introduction = request.data.get("introduction",None)
        if introduction is not None:
            request.user.introduction = introduction

        request.user.save()

        return Response(status=200)


class UserOverview(APIView):

    def post(self,request,*args,**kwargs):
        userid = request.data.get("userid",None)
        EMUsername = request.data.get("emusername",None)
        try:
            if userid is not None:
                user = MyUser.objects.get(pk=userid)
            else:
                user = MyUser.objects.get(EMUser__iexact=EMUsername)
        except MyUser.DoesNotExist:
            return Response({"error":"用户不存在"},status=400)
        ret = OrderedDict()
        ret['id'] = user.pk
        ret['nickname'] = user.nickname
        ret['avatar'] = user.avatar
        ret['posted'] = user.postedProductCount()
        ret['transaction'] = user.totalTransactionCount()
        ret['goodfeedback'] = user.goodFeedBackCount()
        ret['emusername'] = user.EMUser
        if user.gender is not None:
            ret['gender'] = user.gender
        if user.location is not None:
            ret['location'] = user.location
        if user.introduction is not None:
            ret['introduction'] = user.introduction
        return(Response(ret,status=200))

class UserPostedProduct(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = pagination.PageNumberPagination
    
    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        userid = self.request.data["user"]
        try:
            user = MyUser.objects.get(pk=userid)
        except MyUser.DoesNotExist:
            return Response({"error":"用户不存在"},status=400)

        return user.getPostedProduct()

class SelfInfo(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def get(self,request,*args,**kwargs):
        user = request.user
        ret = OrderedDict()
        ret['id'] = user.pk
        ret['nickname'] = user.nickname
        ret['avatar'] = user.avatar
        ret['posted'] = user.postedProductCount()
        ret['bought'] = user.boughtOrderCount()
        ret['sold'] = user.soldOrderCount()
        ret['ordered'] = user.orderedOrderCount()
        ret['pendingbuy'] = user.pendingBuyOrderCount()
        ret['pendingsell'] = user.pendingSellOrderCount()
        ret['awaiting'] = user.awaitingAcceptOrderCount()
        return Response(ret,status=200)



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
    pagination_class = pagination.PageNumberPagination

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

class OrderProduct(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def post(self,request,*args,**kwargs):
        id = request.data["productid"]
        amount = request.data.get("amount",1)
        try:
            product = Product.objects.get(pk=id)
        except Product.DoesNotExist:
            data = {"error":"商品不存在"}
            return Response(data,status=400)
        if OrderMembership.objects.filter(product=product,user=request.user).count()>0:
            data = {"error":"您已经求购个过该产品了"}
            return Response(data,status=400)

        if product.amount-product.soldAmount<amount:
            data = {"error":"商品库存不足"}
            return Response(data,status=400)

        if product.user==request.user:
            data={"error":"不能求购自己的商品"}
            return Response(data,status=400)

        order = OrderMembership(product=product,user = request.user,amount = amount)
        order.save()
        return Response({},status=200)

class BuyProduct(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def post(self,request,*args,**kwargs):
        id = request.data["productid"]
        userids = request.data["userid"]
        try:
            product = Product.objects.get(pk=id)
        except Product.DoesNotExist:
            data = {"error":"商品不存在"}
            return Response(data,status=400)


        for userid in userids:
            buyer = MyUser.objects.get(pk=userid)
            order = buyer.orderedProducts.get(product=product)
            product.soldAmount += order.amount
            order.accepted = True
            order.save()

        return Response(status=200)


class FinishTransactionProduct(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def post(self,request,*args,**kwargs):
        id = request.data["productid"]
        userid = request.data["userid"]
        try:
            product = Product.objects.get(pk=id)
        except Product.DoesNotExist:
            data = {"error":"商品不存在"}
            return Response(data,status=400)

        if product.user==request.user:
            data={"error":"不能买自己的商品"}
            return Response(data,status=400)

        buyer = MyUser.obects.get(pk=userid)
        product.buyer.remove(buyer)
        product.boughtBy.add(buyer)
        product.save()
        return Response(status=200)
    
class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryList(VersionedListCreateAPIView):
    queryset = PrimaryCategory.objects.all()
    serializer_class = PriCatSerializer

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
           # if store.code!=request.data["code"]:
                #wrong verification code
            #    return Response({"error":"验证码不正确"},status=400)
        except EmailCode.DoesNotExist:
            #code expired
            return Response({"error":"验证码已过期，请重新获取"},status=400)
        
        email = request.data["email"]
        #check email not exist
        if MyUser.objects.filter(email__iexact=email).exists():
            #duplicate email
            return Response({"error":"邮箱地址已被注册"},status=400)

        nickname = request.data["nickname"]

        #check nickname not exist
        if MyUser.objects.filter(nickname__iexact=nickname).exists():
            #duplicate nickname
            return Response({"error":"昵称已被使用"},status=400)

        res = super(UserRegister,self).post(request,args,kwargs)
        
        if res.status_code<400:
            #register for EM
            emusername = verifycodegenerator(size=20)
            while MyUser.objects.all().filter(EMUser=emusername).exists():
                emusername = verifycodegenerator(size=20)
        
            #username is now unique
            empassword = verifycodegenerator(size=10)

            createEMaccount(email,emusername,empassword,nickname)
        return res
