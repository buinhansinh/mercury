'''
Created on Aug 29, 2012

@author: bratface
'''
from addressbook.models import Contact
from django.utils import unittest
from trade.models import Order, OrderItem
from inventory.models import Location, StockTransfer, StockTransferItem
from datetime import datetime
from catalog.models import Product, Service


class OrderTestCase(unittest.TestCase):
    
    def setUp(self):
        self.john = Contact.objects.create(name="John's Hardware")
        self.jane = Contact.objects.create(name="Jane's Superstore")
        self.john_office = Location.objects.create(owner=self.john, name="John's Office")
        self.john_warehouse = Location.objects.create(owner=self.john, name="John's Warehouse")
        self.jane_office = Location.objects.create(owner=self.jane, name="Jane's Office")
        self.jane_warehouse = Location.objects.create(owner=self.jane, name="Jane's Warehouse")
    
        def create_product(brand, model, summary):
            return Product.objects.create(brand=brand, model=model, summary=summary)
            
        self.wrench = create_product('BOSS', 'ABC', 'WRENCH',)
        self.screwdriver = create_product('BOSS', 'DEF', 'SCREWDRIVER',)
        self.pliers = create_product('BOSS', 'GHI', 'PLIERS',)
        
        def create_service(name):
            return Service.objects.create(name=name)
        
        self.delivery = create_service('Delivery')        
    
    def testCompletion(self):
        # place an order
        order = Order(supplier=self.john, customer=self.jane, date=datetime.now(), code='1', value=0)
        order.save()
        o_wrench = OrderItem.objects.create(order=order, info=self.wrench, quantity=10, price=10)
        o_screwdriver = OrderItem.objects.create(order=order, info=self.screwdriver, quantity=20, price=20)
        o_pliers = OrderItem.objects.create(order=order, info=self.pliers, quantity=30, price=30)
        
        transfer = StockTransfer.objects.create(origin=self.john_warehouse, 
                                           destination=self.jane_warehouse, 
                                           date=datetime.now(), 
                                           code='1')
        StockTransferItem.objects.create(order=o_wrench, product=self.wrench, transfer=transfer, quantity=10)
        StockTransferItem.objects.create(order=o_screwdriver, product=self.screwdriver, transfer=transfer, quantity=20)
        StockTransferItem.objects.create(order=o_pliers, product=self.pliers, transfer=transfer, quantity=30)
        
        order.evaluate()
        self.assertTrue(order.has_label(Order.CLOSED))
