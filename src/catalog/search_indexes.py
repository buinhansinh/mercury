'''
Created on Dec 26, 2011

@author: bratface
'''

from catalog.models import Product, Service
from haystack import site as haystack
from haystack.fields import CharField, EdgeNgramField
from haystack.indexes import RealTimeSearchIndex
from common.models import Object


class ProductIndex(RealTimeSearchIndex):
    name = EdgeNgramField(model_attr='name', boost=1.25)
    summary = EdgeNgramField(model_attr='summary', null=True)
    text = EdgeNgramField(document=True, use_template=True, template_name='catalog/haystack/product_text.txt')
    html = CharField(use_template=True, template_name='catalog/haystack/product_result.html')
    class Meta:
        pass

    def should_update(self, instance, **kwargs):
        update = not instance.labeled(Object.ARCHIVE)
        if not update:
            self.remove_object(instance, **kwargs)
        return update


class ServiceIndex(RealTimeSearchIndex):
    name = EdgeNgramField(model_attr='name', boost=1.25)
    summary = EdgeNgramField(model_attr='summary', null=True)
    text = EdgeNgramField(document=True, use_template=True, template_name='catalog/haystack/service_text.txt')
    html = CharField(use_template=True, template_name='catalog/haystack/service_result.html')
    class Meta:
        pass

    def should_update(self, instance, **kwargs):
        update = not instance.labeled(Object.ARCHIVE)
        if not update:
            self.remove_object(instance, **kwargs)
        return update


haystack.register(Product, ProductIndex)
haystack.register(Service, ServiceIndex)