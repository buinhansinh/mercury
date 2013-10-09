'''
Created on Dec 26, 2011

@author: bratface
'''

from haystack import site as haystack
from haystack.fields import CharField, EdgeNgramField
from haystack.indexes import RealTimeSearchIndex
from inventory.models import Location


class LocationIndex(RealTimeSearchIndex):
    name = EdgeNgramField(model_attr='name')
    text = EdgeNgramField(document=True, use_template=True, template_name='inventory/haystack/location_text.txt')
    html = CharField(use_template=True, template_name='inventory/haystack/location_result.html')
    class Meta:
        pass


haystack.register(Location, LocationIndex)