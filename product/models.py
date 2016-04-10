from __future__ import unicode_literals
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

class EmailCode(models.Model):
    code = models.CharField(max_length=5)

class ProductQuerySet(models.query.QuerySet):
    def nearby(self,latitude,longitude,distance):
        gcd = '6371 * acos(cos(radians(%s)) * cos(radians(latitude))*cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))'
        gcd_lt = "{} < %s".format(gcd)
        return self.extra(
                    select={'distance':gcd},
                    select_params=[latitude,longitude,latitude],
                    where=[gcd_lt],
                    params=[latitude,longitude,latitude,distance],
                    order_by=['distance']
                    )

    def orderByPriceAscending(self):
        return self.order_by('price')

    def orderByPriceDescending(self):
        return self.order_by('-price')

    def orderByPostTime(self):
        return self.order_by('-postedTime')

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(model=self.model, using=self._db)

    def nearby(self, latitude, longitude, distance):
        return self.get_queryset().nearby(latitude,longitude,distance)

    def orderByPriceAscending(self):
        return self.get_queryset().orderByPriceAscending()

    def orderByPriceDescending(self):
        return self.get_queryset().orderByPriceDescending()
    
    def orderByPostTime(self):
        return self.get_queryset().orderByPostTime()

class Product(models.Model):
    title = models.CharField(max_length=20, blank=True, default='')
    mainimage = models.IntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    location = models.CharField(max_length=5)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=20)
    country = models.CharField(max_length=10)
    amount = models.IntegerField()
    category = models.ForeignKey('SecondaryCategory', on_delete=models.SET_NULL,null=True)
    postedTime = models.DateTimeField(auto_now_add=True)
    originalPrice = models.DecimalField(max_digits=10,decimal_places=2, null=True)
    brandNew = models.NullBooleanField()
    bargain = models.NullBooleanField()
    exchange = models.NullBooleanField()
    description = models.TextField(blank=True, default='')
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='products',on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='boughtProducts',on_delete=models.SET_NULL,null=True)

    objects = ProductManager()

class ImageUUID(models.Model):
	product = models.ForeignKey('Product',on_delete=models.CASCADE,related_name='images')
	uuid = models.CharField(max_length=40)

class Version(models.Model):
    version = models.IntegerField()

class PrimaryCategory(models.Model):
    title = models.CharField(max_length=10)
    icon = models.CharField(max_length=40, blank=True, default='')
    icon_naked = models.CharField(max_length=40,blank=True,default='')
    version = models.ForeignKey(Version,default=1)

class SecondaryCategory(models.Model):
    title = models.CharField(max_length=10)
    primaryCategory = models.ForeignKey(PrimaryCategory, related_name='secondary')

class MyUserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(Q(email__iexact=username)|Q(nickname__iexact=username))
    def create_user(self,email,password,nickname,**extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,nickname=nickname,date_joined=now,last_login=now,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,nickname,password,**extra_fields):
        user = self.create_user(email,nickname=nickname,password=password,**extra_fields)
        user.is_admin = True
        user.save(using=self._db)
        return user

class MyUser(AbstractBaseUser):
    email = models.EmailField(max_length=254,unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    nickname = models.CharField(max_length=254,unique=True)
    avatar = models.CharField(max_length=50,default="default")

    EMUser = models.CharField(max_length=20,null=True)
    EMPass = models.CharField(max_length=10,null=True)
    
    gender = models.IntegerField(null=True)
    location = models.CharField(max_length=100,null=True)
    introduction = models.CharField(max_length=200,null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname',]
    
    objects = MyUserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    def getPostedProducts(self):
        return Product.objects.all().filter(user=self).order_by("-postedTime")

    def getSoldProduct(self):
        return Product.objects.all().filter(user=self).filter(buyer__isnull=False).order_by("-postedTime")
    def getBoughtProduct(self):
        return Product.objects.all().filter(buyer=self).order_by("-postedTime")

    def totalTransactionCount(self):
        return self.boughtProductCount()+self.soldProductCount()

    def goodFeedBackCount(self):
        sentGood = self.sentFeedbacks.filter(rating=0).count()
        receivedGood = self.receivedFeedbacks.filter(rating=0).count()
        return sentGood+receivedGood

    def postedProductCount(self):
        return self.products.count()

    def boughtProductCount(self):
        return self.boughtProducts.count()

    def soldProductCount(self):
        return self.products.filter(buyer__isnull=False).count()

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self,app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

class FeedBack(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,related_name="sentFeedbacks",null=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,related_name="receivedFeedbacks",null=True)
    content = models.CharField(max_length = 255)
    product = models.ForeignKey(Product,related_name="feedback",on_delete=models.SET_NULL,null=True)
    #rating 0-good 1-medium 2-bad
    rating = models.IntegerField()

