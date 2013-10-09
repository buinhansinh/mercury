'''
Created on Dec 7, 2011

@author: bratface
'''
from common.models import Object, Enum
from django.db import models
from taggit.managers import TaggableManager
import common.fields


class ProductManager(models.Manager):
    pass


class Product(Object):
    SERVICE = Enum('service')
    
    objects = ProductManager()

    brand = common.fields.LabelField()
    model = common.fields.LabelField()
    summary = common.fields.MessageField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    
    @staticmethod
    def create(brand, model, summary='', tags=''):
        #ensure uniqueness
        product, created = Product.objects.get_or_create(brand=brand, model=model)
        if created:
            product.summary = summary
            product.tags = tags
            product.save()
            return Product
        else:
            return None

    def name(self):
        return '%s %s' % (self.brand, self.model)
    
    
class ServiceManager(models.Manager):
    pass


class Service(Object):
    objects = ServiceManager()

    name = common.fields.LabelField(unique=True)
    summary = common.fields.MessageField(null=True, blank=True)
    tags = TaggableManager(blank=True)

    @staticmethod
    def create(name, summary='', tags=''):
        Service.objects.create(name=name, summary=summary)


#class Assembly(models.Model):
#    name = common.fields.LabelField(unique=True)
#    summary = common.fields.MessageField(null=True, blank=True)
#    description = models.TextField(null=True, blank=True)
#    tags = TaggableManager(blank=True)
#
#
#class AssemblyItem(models.Model):
#    order = models.ForeignKey(Assembly, related_name='items')
#    number = models.SmallIntegerField(default=0)
#    quantity = common.fields.DecimalField()
#    info_type = models.ForeignKey(ContentType)
#    info_id = models.PositiveIntegerField()    
#    info = generic.GenericForeignKey('info_type', 'info_id')
