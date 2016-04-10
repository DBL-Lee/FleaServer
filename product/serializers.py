from rest_framework import serializers
from product.models import Product,ImageUUID,PrimaryCategory,SecondaryCategory,MyUser,EmailCode,FeedBack
from django.contrib.auth import get_user_model

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = ('id','sender','product','receiver','content','rating')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id','email','nickname','EMUser','EMPass','password','avatar','gender','location','introduction')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(email=validated_data['email'],nickname=validated_data['nickname'],password=validated_data['password'])

        return user

class ImageUUIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUUID
        fields = ('uuid',)


class ProductSerializer(serializers.ModelSerializer):
    images = ImageUUIDSerializer(many=True) 
    category = serializers.PrimaryKeyRelatedField(queryset=SecondaryCategory.objects.all())
    usernickname = serializers.ReadOnlyField(source='user.nickname')
    useravatar = serializers.ReadOnlyField(source='user.avatar')
    userid = serializers.ReadOnlyField(source='user.pk')


    class Meta:
        model = Product
        fields = ('id','usernickname','useravatar','userid','title','mainimage','city','country','images','category','price','location','latitude','longitude','amount','postedTime','originalPrice','brandNew','bargain','exchange','description')
        
    def create(self, validated_data):
        user = self.context['request'].user
        images = validated_data.pop('images')
        product = Product.objects.create(user=user,**validated_data)
        for image in images:
            ImageUUID.objects.create(product=product,**image)
        return product

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title',instance.title)
        instance.price = validated_data.get('price',instance.price)
        instance.location = validated_data.get('location',instance.location)
        instance.amount = validated_data.get('amount',instance.amount)
        instance.longitude = validated_data.get('longitude',instance.longitude)
        instance.latitude = validated_data.get('latitude',instance.latitude)
        instance.originalPrice = validated_data.get('originalPrice',instance.originalPrice)
        instance.brandNew = validated_data.get('brandNew',instance.brandNew)
        instance.bargain = validated_data.get('bargain',instance.bargain)
        instance.exchange = validated_data.get('exchange',instance.exchange)
        instance.description = validated_data.get('description',instance.description)
        cat = SecondaryCategory.objects.get(pk=validated_data['category'])
        instance.category = cat
        for image in instance.images.all():
            image.delete()
        images = validated_data.pop('images')
        for image in images:
            ImageUUID.objects.create(product=instance,**image)
        instance.save()
        return instance

class SecCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondaryCategory
        fields = ('id','title',)

class PriCatSerializer(serializers.ModelSerializer):
    secondary = SecCatSerializer(many=True)

    class Meta:
        model = PrimaryCategory
        fields = ('id','icon','icon_naked','title','secondary',)

    def create(self, validated_data):
        secondaries = validated_data.pop('secondary')
        primary = PrimaryCategory.objects.create(**validated_data)
        for secondary in secondaries:
            SecondaryCategory.objects.create(primaryCategory=primary,**secondary)
        return primary

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title',instance.title)
        instance.icon = validated_data.get('icon',instance.icon)
        for secondary in instance.secondary.all():
            secondary.delete()
        for secondary in validated_data.pop('secondary'):
            SecondaryCategory.objects.create(primaryCategory=instance,**secondary)
        instance.save()
        return instance
