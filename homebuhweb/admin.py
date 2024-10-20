from django.contrib import admin
from .models import Profile
from .models import (Category, SubCategory,
                     SubSubCategory, Expense,
                     Income, CarExpense, PlannedExpense, Credit)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'phone', 'address')


admin.site.register(CarExpense)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Income)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(SubSubCategory)
admin.site.register(Expense)
admin.site.register(PlannedExpense)
admin.site.register(Credit)
