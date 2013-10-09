'''
Created on Dec 29, 2012

@author: bratface
'''
from django.contrib import admin
from company.models import UserAccount

class UserAccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserAccount, UserAccountAdmin)