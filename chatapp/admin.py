from django.contrib import admin
from .models import Message, UserChat

# Register your models here.

admin.site.register(UserChat)
admin.site.register(Message)
