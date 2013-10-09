'''
Created on Jan 31, 2013

@author: terence
'''
from django.core.management.base import NoArgsCommand
from company.models import ItemAccount


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        accounts = ItemAccount.objects.all()
        for a in accounts:
            a.assess()