from django.contrib import admin
from .models import Profile
from .models import Category, SubCategory, SubSubCategory, Expense, Income


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'phone', 'address')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Income)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(SubSubCategory)
admin.site.register(Expense)
