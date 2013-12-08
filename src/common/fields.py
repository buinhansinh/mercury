'''
Created on Oct 6, 2010

@author: Terence
'''

from decimal import Decimal
from django.db import models


class LabelField(models.CharField):
    description = 'A field for labeling an object. Just for consistency.'
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 64
        super(models.CharField, self).__init__(*args, **kwargs)


class MessageField(models.CharField):
    description = 'A multi-purpose message field'
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 160
        super(models.CharField, self).__init__(*args, **kwargs)


class DiscountField(models.CharField):
    description = "A field for ridiculously long discount chains perpetuated by the industry (e.g. -50-10-5)."
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 128
        super(models.CharField, self).__init__(*args, **kwargs)


class DecimalField(models.DecimalField):
    description = "A field that complies neatly with human notions of quantity and currency for accounting purposes"

    @staticmethod
    def fromString(string):
        return Decimal(0 if string == '' else string)
    
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 15
        kwargs['decimal_places'] = 2 
        super(DecimalField, self).__init__(*args, **kwargs)
        

class PrecisionDecimalField(models.DecimalField):
    description = "A field that complies neatly with human notions of quantity and currency for accounting purposes"

    @staticmethod
    def fromString(string):
        return Decimal(0 if string == '' else string)
    
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 15
        kwargs['decimal_places'] = 3
        super(PrecisionDecimalField, self).__init__(*args, **kwargs)


class EnumField(models.BigIntegerField):
    description = "A field for storing enum fields. Used in conjunction with Enum() to hash a string."

    def __init__(self, *args, **kwargs):
        kwargs['default'] = 0
        super(models.BigIntegerField, self).__init__(*args, **kwargs)    


class PercentageField(models.DecimalField):
    description = ''
    
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 4
        kwargs['decimal_places'] = 2
        kwargs['null'] = False
        kwargs['blank'] = False
        kwargs['default'] = 0
        super(PercentageField, self).__init__(*args, **kwargs)        
