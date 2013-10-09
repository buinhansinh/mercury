'''
Created on Oct 6, 2010

@author: Terence
'''
from common.models import Enum, Object
from django.db import models
from taggit.managers import TaggableManager
import common.fields


class ContactManager(models.Manager):
    pass


class Contact(Object):
    objects = ContactManager()
   
    name = common.fields.LabelField(unique=True)
    notes = models.TextField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    
    def summary(self):
        addresses = self.addresses()
        if addresses.count() > 0:
            return addresses[0].value
        else:
            return ''
    
    def numbers(self):
        return self.details.filter(type=ContactDetail.NUMBER)
    
    def addresses(self):
        return self.details.filter(type=ContactDetail.ADDRESS)
    
    def emails(self):
        return self.details.filter(type=ContactDetail.EMAIL)
    
    def links(self):
        return self.details.filter(type=ContactDetail.LINK)
        
    def other_details(self):
        return self.details.filter(type=ContactDetail.OTHER)
    
    def __unicode__(self):
        return u'%s' % (self.name)


class ContactDetail(models.Model):
    NUMBER = Enum('number')
    ADDRESS = Enum('address')
    EMAIL = Enum('email')
    LINK = Enum('link')
    OTHER = Enum('other')
    
    owner = models.ForeignKey(Contact, null=False, blank=False, related_name='details')
    type = common.fields.EnumField()
    label = models.CharField(max_length=32, blank=True)
    value = models.TextField(blank=False)

    def __unicode__(self):
        return u'%s' % (self.value)   
