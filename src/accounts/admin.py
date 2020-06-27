from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name')
    fields = (
        'email',
        'name',
        'is_staff',
        'is_superuser',
        'is_active',
        'is_email_verified',
    )
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('name',)


# turn off displaying django groups that are not used in project
admin.site.unregister(Group)
