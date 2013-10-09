'''
Created on Apr 9, 2012

@author: bratface
'''
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
import common.fields
import django.dispatch
import zlib


"""
  Instead of using consecutive numbers, which become unwieldly as we add enum values, we use a hash.
  A hash is guaranteed unique for a given sequence and since enumeration value sets are small,
  clashes won't be a problem.  Hopefully.  Probably.
"""
def Enum(name):
    return zlib.adler32(name)


class LabeledItem(models.Model):
    name = common.fields.EnumField()
    item_type = models.ForeignKey(ContentType)
    item_id = models.PositiveIntegerField()
    item = generic.GenericForeignKey('item_type', 'item_id')
    date = models.DateTimeField(auto_now_add=True)


class LabelRelation(generic.GenericRelation):
    def __init__(self, *args, **kwargs):
        super(LabelRelation, self).__init__(LabeledItem, content_type_field='item_type', object_id_field="item_id")


class Labelable:
    """
    Returns a label if it exists, False otherwise
    """
    def labeled(self, label):
        if self.labels.filter(name=label).exists():
            return self.labels.get(name=label)
        else:
            return False
    
    def label(self, label):
        if not self.labeled(label):
            new_label = LabeledItem()
            new_label.name = label
            new_label.item = self
            new_label.save()
    
    def label_if(self, condition, label):
        self.label(label) if condition else self.unlabel(label)
    
    def unlabel(self, label):
        try:
            label = self.labels.get(name=label)
            label.delete()
        except:
            pass


class ObjectLog(models.Model):
    action = common.fields.EnumField()

    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('object_type', 'object_id')

    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)


class Object(models.Model, Labelable):
    class Meta:
        abstract = True

    Event = django.dispatch.Signal()

    REGISTER = Enum('register')
    ARCHIVE = Enum('archive')

    labels = LabelRelation()
    logs = generic.GenericRelation(ObjectLog, content_type_field='object_type', object_id_field="object_id")

    def date_registered(self):
        try:
            log = self.logs.get(action=Object.REGISTER)
            return log.date
        except ObjectLog.DoesNotExist:
            return None
    
#    def date_updated(self):
#        try:
#            log = self.logs.filter(action=Object.UPDATED).latest('date')
#            return log.date
#        except ObjectLog.DoesNotExist:
#            return None

    def date_archived(self):
        try:
            log = self.logs.get(action=Object.ARCHIVE)
            return log.date
        except ObjectLog.DoesNotExist:
            return None

    def log(self, action, user):
        self_type = ContentType.objects.get_for_model(self)
        self.logs.create(action=action, user=user, object_id=self.id, object_type=self_type)
        Object.Event.send(sender=self.__class__, instance=self, action=action, user=user)

    @models.permalink
    def get_view_url(self):
        self_type = ContentType.objects.get_for_model(self)
        return ('%s.views.%s.view' % (self_type.app_label, self_type.model), (), {'_id': self.id})

    @models.permalink
    def get_edit_url(self):
        self_type = ContentType.objects.get_for_model(self)
        return ('%s.views.%s.edit' % (self_type.app_label, self_type.model), (), {'_id': self.id} )
    
    @models.permalink
    def get_archive_url(self):
        self_type = ContentType.objects.get_for_model(self)
        return ('%s.views.%s.archive' % (self_type.app_label, self_type.model), (), {'_id': self.id} )
    
    @classmethod
    def content_type(cls):
        return ContentType.objects.get_for_model(cls)
    

class Document(Object):
    class Meta:
        abstract = True
    
    # actions
    CHECKIN = Enum('checkin')
    CHECKOUT = Enum('checkout')
    CANCEL = Enum('cancel')
    
    # labels
    VALID = Enum('valid')
    CANCELED = Enum('canceled')
    
    date = models.DateTimeField(blank=True)
    code = common.fields.LabelField(blank=True)

    def clean(self):
        if self.date == None:
            date = self.date_registered()
            if date:
                self.date = date
            else:
                self.date = datetime.now()
        super(Document, self).clean()

    def save(self, *args, **kwargs):
        Document.clean(self)
        super(Document, self).save(*args, **kwargs)

    def reference(self):
        if self.id:
            return "%s-%04.f" % (self.date_registered().strftime('%y%m%d'), self.id)
        else:
            return None
    
    def canceled(self):
        return self.labeled(Document.CANCELED)
        
    @models.permalink
    def get_cancel_url(self):
        self_type = ContentType.objects.get_for_model(self)
        return ('%s.views.%s.cancel' % (self_type.app_label, self_type.model), (), {'_id': self.id} )
