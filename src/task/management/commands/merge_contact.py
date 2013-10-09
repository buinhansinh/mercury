'''
Created on Feb 6, 2013

@author: bratface
'''
from task.util import merge_contacts
from django.core.management.base import BaseCommand
from addressbook.models import Contact


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        c1 = Contact.objects.get(pk=args[0])
        c2 = Contact.objects.get(pk=args[1])
        merge_contacts(c1, c2)