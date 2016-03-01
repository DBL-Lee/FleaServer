from django.conf.urls import url
from product import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
	url(r'^products/$',views.ProductList.as_view()),
	url(r'^products/(?P<pk>[0-9]+)/$',views.ProductDetail.as_view()),
    url(r'^products/primarycategory/$',views.CategoryList.as_view()),
    url(r'^products/primarycategory/(?P<pk>[0-9]+)/$',views.CategoryDetail.as_view()),
    url(r'^products/primarycategory/version/$',views.currentVersion),
]

urlpatterns = format_suffix_patterns(urlpatterns)
