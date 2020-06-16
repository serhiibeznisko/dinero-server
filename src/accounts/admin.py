from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User


# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     readonly_fields = ('created_at', 'updated_at')


# turn off displaying django groups that are not used in project
admin.site.unregister(Group)
