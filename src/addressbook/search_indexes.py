'''
Created on Dec 26, 2011

@author: bratface
'''

from addressbook.models import Contact
from haystack import site as haystack
from haystack.fields import CharField, EdgeNgramField
from haystack.indexes import RealTimeSearchIndex
from common.models import Object


class ContactIndex(RealTimeSearchIndex):
    class Meta:
        pass

    name = EdgeNgramField(model_attr='name')
    summary = EdgeNgramField(model_attr='summary', null=True)
    text = EdgeNgramField(document=True, use_template=True, template_name='addressbook/haystack/contact_text.txt')
    html = CharField(use_template=True, template_name='addressbook/haystack/contact_result.html')
   
    def should_update(self, instance, **kwargs):
        update = not instance.labeled(Object.ARCHIVE)
        if not update:
            self.remove_object(instance, **kwargs)
        return update

haystack.register(Contact, ContactIndex)