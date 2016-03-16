from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import MyUser
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth import get_user_model

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = '__all__'

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = '__all__'

class MyUserAdmin(BaseUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    list_display = ('email',)
    list_filter = ()
    fieldsets = ((None,{'fields':('email','password')}),)

    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(MyUser, MyUserAdmin)
admin.site.unregister(Group)
# Register your models here.
