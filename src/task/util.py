'''
Created on Sep 13, 2013

@author: terence
'''
from accounting.models import Bill, Payment, Expense
from addressbook.models import ContactDetail
from catalog.models import Product
from company.models import ItemAccount, UserAccount, CompanyAccount, \
    TradeAccount
from django.db.models.query_utils import Q
from inventory.models import Stock, AdjustmentItem, StockTransferItem, Location, \
    StockTransaction
from trade.models import OrderItem, Order, OrderTransfer


def merge_products(p1, p2):
    # Order items
    items = OrderItem.objects.filter(info_id=p1.id, info_type=Product.content_type())
    for i in items:
        i.info_id = p2.id
        i.save()
        
    # Adjustment item
    items = AdjustmentItem.objects.filter(product=p1)
    for i in items:
        i.product = p2
        i.save()
    
    # Stock transfer item
    items = StockTransferItem.objects.filter(product=p1)
    for i in items:
        i.product = p2
        i.save()
    
    # Stock
    stocks = Stock.objects.filter(product=p1)
    for s1 in stocks:
        s2, _ = Stock.objects.get_or_create(product=p2, location=s1.location)
        merge_stocks(s1, s2)
        
    # ItemAccount
    accounts = ItemAccount.objects.filter(item_id=p1.id, item_type=p1.content_type())
    for a in accounts:
        p2_account, _ = ItemAccount.objects.get_or_create(item_id=p2.id, item_type=p2.content_type(), owner=a.owner)
        p2_account.stock += a.stock
        if p2_account.cost == 0: p2_account.cost = a.cost
        if p2_account.price == 0: p2_account.price = a.price
        p2_account.save()
        a.delete()
    
    p1.delete()


def merge_contacts(c1, c2):
    details = ContactDetail.objects.filter(owner=c1)
    for d in details:
        d.owner = c2
        d.save()
        
    uas = UserAccount.objects.filter(company=c1)
    for ua in uas:
        ua.company = c2
        ua.save()
        
    # company account
    try:
        ca = CompanyAccount.objects.get(contact=c1)
        ca.delete()
    except CompanyAccount.DoesNotExist:
        pass
    
    def move(clazz):
        txns = clazz.objects.filter(Q(supplier=c1) | Q(customer=c1))
        for t in txns:
            if t.supplier == c1:
                t.supplier = c2
                t.save()
            elif t.customer == c1:
                t.customer = c2
                t.save()
    
    # orders
    move(Order)
    # bill
    move(Bill)
    # payment
    move(Payment)
    # expense
    
    es = Expense.objects.filter(Q(owner=c1) | Q(contact=c1))
    for e in es:
        if e.owner == c1:
            e.owner = c2
            e.save()
        elif e.contact == c1:
            e.contact = c2
            e.save()    
    
    # trade account
    # copy over debt and credit        
    tas1 = TradeAccount.objects.filter(Q(supplier=c1) | Q(customer=c1))
    for ta1 in tas1:
        if ta1.supplier == c1:
            try:
                ta2 = TradeAccount.objects.get(supplier=c2, customer=ta1.customer)
                ta2.debt += ta1.debt
                ta2.credit += ta1.credit
                ta2.save()
                ta1.delete()
            except TradeAccount.DoesNotExist:
                ta1.supplier = c2
                ta1.save()
        elif ta1.customer == c1:
            try:
                ta2 = TradeAccount.objects.get(customer=c2, supplier=ta1.supplier)
                ta2.debt += ta1.debt
                ta2.credit += ta1.credit
                ta2.save()
                ta1.delete()
            except TradeAccount.DoesNotExist:
                ta1.customer = c2
                ta1.save()        
    
    # location
    # copy over 'Default', otherwise doble
    try:
        l1 = c1.locations.get(name=Location.DEFAULT)
    except Location.DoesNotExist:
        l1 = None
    try:
        l2 = c2.locations.get(name=Location.DEFAULT)
    except:
        l2 = None
    
    if l1 and l2:
        merge_locations(l1, l2)
    elif l1:
        l1.owner = c2
    c1.delete()


def merge_locations(l1, l2):
    # order transfer
    ots = OrderTransfer.objects.filter(Q(origin=l1) | Q(destination=l1))
    for ot in ots:
        if ot.origin == l1:
            ot.origin = l2
            ot.save()
        elif ot.destination == l1:
            ot.destination = l2
            ot.save()
    # stock
    ss = Stock.objects.filter(location=l1)
    for s1 in ss:
        try:
            s2 = Stock.objects.get(product=s1.product, location=l2)
            merge_stocks(s1, s2)
        except Stock.DoesNotExist:
            s1.location = l2
            s1.save()
    l1.delete()


def merge_stocks(s1, s2):
    # stock transaction
    sts = StockTransaction.objects.filter(stock=s1)
    for st in sts:
        st.stock = s2
        st.save()
    s2.quantity += s1.quantity
    s2.save()
    s1.delete()