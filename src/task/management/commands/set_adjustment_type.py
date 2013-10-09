'''
Created on Jan 31, 2013

@author: terence
'''
from django.core.management.base import NoArgsCommand
from inventory.models import Adjustment


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        adjustments = Adjustment.objects.all()
        for a in adjustments:
            a.type = Adjustment.ASSEMBLY
            a.save()