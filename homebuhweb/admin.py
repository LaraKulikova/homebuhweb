from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'financial_report')


admin.site.register(UserProfile, UserProfileAdmin)
