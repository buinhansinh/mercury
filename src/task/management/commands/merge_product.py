'''
Created on Feb 6, 2013

@author: bratface
'''
from task.util import merge_product
from django.core.management.base import BaseCommand
from catalog.models import Product


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        p1 = Product.objects.get(pk=args[0])
        p2 = Product.objects.get(pk=args[1])
        merge_product(p1, p2)