'''
Created on Feb 1, 2013

@author: terence
'''
from django.core.management.base import LabelCommand
from accounting.models import Bill, Payment
from common.models import Document


class Command(LabelCommand):
    
    def handle_label(self, label, **options):
        clazz = Payment
        obj = clazz.objects.get(pk=label)
        for log in obj.logs.all():
            if log.action == Document.REGISTER: action = 'register'
            elif log.action == Document.CHECKIN: action = 'checkin'
            elif log.action == Document.CHECKOUT: action = 'checkout'
            print "{} {} {}".format(log.user, log.date, action)
        