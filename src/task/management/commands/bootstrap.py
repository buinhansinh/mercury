'''
Created on Jul 20, 2012

@author: bratface
'''
from addressbook.models import Contact, ContactDetail
from catalog.models import Product, Service
from django.contrib.auth.models import Group, User
from django.core.management.base import NoArgsCommand
from django.db import transaction
from inventory.models import Location, Stock
from trade.models import OrderItem, Order
from datetime import datetime
import settings
from company.models import CompanyAccount


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        with transaction.commit_on_success():        
            # create an admin
            admin = User(username='admin')
            admin.set_password('pass')
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            
            # create them groups
            Group.objects.get_or_create(name="sales")
            Group.objects.get_or_create(name="purchasing")
            Group.objects.get_or_create(name="inventory")
            Group.objects.get_or_create(name="accounting")
            Group.objects.get_or_create(name="management")
            
            # create the company
            company = Contact.objects.create(name='My Company')
            CompanyAccount.objects.create(contact=company, 
                                          cutoff_date=datetime(year=datetime.today().year,
                                                          month=1,
                                                          day=1))
            
            # generate a default location
#            Location.objects.create(owner=company,
#                                    name='My Location',
#                                    address='My Address')
            
            # attach it to the admin
            profile = admin.get_profile()
            profile.company = company
            profile.save()
        
            if False:
                self.filldb(admin)
        pass

    def filldb(self, admin):
        company = admin.get_profile().company

        # contacts
        c = Contact.objects.create(name='John')
        ContactDetail.objects.create(owner=c, type=ContactDetail.NUMBER, label='home', value='123-4567')
        ContactDetail.objects.create(owner=c, type=ContactDetail.ADDRESS, label='home', value='12 Sunshine St')

        c = Contact.objects.create(name='Jane')
        ContactDetail.objects.create(owner=c, type=ContactDetail.NUMBER, label='home', value='123-4567')
        ContactDetail.objects.create(owner=c, type=ContactDetail.ADDRESS, label='home', value='12 Sunset St')

        c = Contact.objects.create(name='Joe')
        ContactDetail.objects.create(owner=c, type=ContactDetail.NUMBER, label='home', value='123-4567')
        ContactDetail.objects.create(owner=c, type=ContactDetail.ADDRESS, label='home', value='12 Moon St.')

        def create_product(brand, model, summary):
            product = Product.objects.create(brand=brand, model=model, summary=summary)
            product.log(Product.REGISTER, admin)
        
        # catalog
        create_product('ANLY', 'AH3NC', 'TIMER',)
        create_product('ANLY', 'AH3NB', 'TIMER',)
        create_product('ANLY', 'AFR-1', 'FLOATLESS RELAY',)
        create_product('ANLY', 'TRD-N', 'WYE-DELTA TIMER',)
        create_product('FUJI', 'SC-0', 'CONTACTOR',)
        create_product('FUJI', 'SC-4-1', 'CONTACTOR',)
        create_product('FUJI', 'SC-5-1', 'CONTACTOR',)
        create_product('FUJI', 'SC-N1', 'CONTACTOR',)
        create_product('BROYCE', 'B8PRC-220', 'OVER-UNDER VOLTAGE RELAY',)
        create_product('BROYCE', 'B8PRC-440', 'OVER-UNDER VOLTAGE RELAY',)
        
        def create_service(name):
            service = Service.objects.create(name=name)
            service.log(Service.REGISTER, admin)
        
        create_service('Control Assembly')
        create_service('Panelboard Assembly')
        create_service('Delivery')
        
        # inventory
        loc = Location.objects.create(owner=company,
                                      name='Location A',
                                      address='Top of the world')
        loc.log(Location.REGISTER, admin)
        loc = Location.objects.create(owner=company,
                                      name='Location B',
                                      address='Bottom of the world')
        loc.log(Location.REGISTER, admin)
        
        # orders
        customer = Contact.objects.get(pk=2)
        product1 = Product.objects.get(pk=1)
        product2 = Product.objects.get(pk=2)
        product3 = Product.objects.get(pk=3)

        def init_stock(location_id, product_id):
            stock = Stock.objects.get(location__id=1, product__id=product_id)
            stock.quantity += 100
            stock.save()
            
        init_stock(1, 1)
        init_stock(1, 2)
        init_stock(1, 3)

        order = Order(customer=customer,
            supplier=company,
            date=datetime.today(),
            code='1234')
        order.save()

        item = OrderItem() #item 1
        item.document = order
        item.price = 99 
        item.quantity = 2
        item.info = product1
        item.order = order
        item.save()
        
        item = OrderItem() #item 2
        item.document = order
        item.price = 16 
        item.quantity = 3
        item.info = product2
        item.order = order
        item.save()
        
        item = OrderItem() #item 2
        item.document = order
        item.price = 33
        item.quantity = 25
        item.info = product3
        item.order = order
        item.save()

        order.log(Order.REGISTER, admin)
        
        pass
