from rest_framework import serializers
from product.models import Product,ImageUUID,PrimaryCategory,SecondaryCategory

class ImageUUIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUUID
        fields = ('uuid',)


class ProductSerializer(serializers.ModelSerializer):
    images = ImageUUIDSerializer(many=True) 
    category = serializers.PrimaryKeyRelatedField(queryset=SecondaryCategory.objects.all())

    class Meta:
        model = Product
        fields = ('id','title','mainimage','city','country','images','category','price','location','gps','amount','postedTime','originalPrice','brandNew','bargain','exchange','description')
        
    def create(self, validated_data):
        images = validated_data.pop('images')
        product = Product.objects.create(**validated_data)
        for image in images:
            ImageUUID.objects.create(product=product,**image)
        return product

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title',instance.title)
        instance.price = validated_data.get('price',instance.price)
        instance.location = validated_data.get('location',instance.location)
        instance.amount = validated_data.get('amount',instance.amount)
        instance.gps = validated_data.get('gps',instance.gps)
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
        fields = ('id','icon','title','secondary',)

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
