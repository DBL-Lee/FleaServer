from rest_framework import status,filters, mixins,generics,pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from product.models import Product,PrimaryCategory,Version
from product.serializers import ProductSerializer,PriCatSerializer
from django.http import HttpResponse
import django_filters

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

class MyCursorPagination(pagination.CursorPagination):
    ordering = '-postedTime'

class ProductFilter(filters.FilterSet):
    min_price = django_filters.NumberFilter(name="price", lookup_type='gte')
    max_price = django_filters.NumberFilter(name="price", lookup_type='lte')
    primarycategory = django_filters.NumberFilter(name="category__primaryCategory__pk")
    secondarycategory = django_filters.NumberFilter(name="category__pk")
    class Meta:
        model = Product
        fields = ['min_price','max_price','primarycategory','secondarycategory','brandNew','bargain','exchange']

class ProductList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    pagination_class = MyCursorPagination
    filter_class = ProductFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        queryset = Product.objects.all()
        titleq = self.request.query_params.get('title',None)
        if titleq is not None:
            queryset = queryset.filter(title__icontains=titleq)
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
