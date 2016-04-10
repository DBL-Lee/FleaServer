
from django.conf.urls import url
from chat import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^chat/sendmessage/',views.SendMessageToUser.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
