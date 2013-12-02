'''
Created on Oct 1, 2012

@author: bratface
'''
from accounting.models import Bill, Payment, Expense, Refund, PaymentAllocation
from addressbook.models import Contact
from catalog.models import Product, Service
from company.models import ItemAccount, TradeAccount
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from inventory.models import Physical, Location, Stock, StockTransfer, \
    Adjustment, StockTransaction
from trade.models import Order, OrderTransfer, OrderReturn
import logging


class WorkflowException(Exception):
    pass


class IntegrityError(Exception):
    pass


"""
    Addressbook Triggers
"""
@receiver(Contact.Event, sender=Contact)
def contact(sender, instance, action, user, **kwargs):
    if action == Contact.ARCHIVE:
        instance.label(Contact.ARCHIVE)
        instance.save()


"""
    Catalog Triggers
"""
@receiver(Product.Event, sender=Product)
def product(sender, instance, action, user, **kwargs):
    if action == Product.REGISTER:
        company = user.account.company
        locations = company.locations.all()
        for l in locations:
            Stock.objects.get_or_create(location=l, product=instance)
        item_type = ContentType.objects.get_for_model(instance) 
        ItemAccount.objects.get_or_create(owner=company, item_type=item_type, item_id=instance.id)
    elif action == Product.ARCHIVE:
        instance.label(Product.ARCHIVE)
        instance.save()


@receiver(Service.Event, sender=Service)
def service(sender, instance, action, user, **kwargs):
    if action == Service.REGISTER:
        company = user.account.company
        item_type = ContentType.objects.get_for_model(instance)
        ItemAccount.objects.get_or_create(owner=company, item_type=item_type, item_id=instance.id)
    elif action == Service.ARCHIVE:
        instance.label(Service.ARCHIVE)
        instance.save()


"""
    Inventory Triggers
"""
@receiver(Location.Event, sender=Location)
def location(sender, instance, action, user, **kwargs):
    if action == Location.REGISTER:
        products = Product.objects.all()
        for p in products:
            Stock.objects.get_or_create(location=instance, product=p)


def create_or_update_txn(stock, quantity, date, action):
    action_type = ContentType.objects.get_for_model(action)
    txn, _ = StockTransaction.objects.get_or_create(stock=stock, 
                                                    action_type=action_type, 
                                                    action_id=action.id, 
                                                    defaults={'date': date,})
    if action.canceled():
        txn.delete()
    else:
        txn.quantity = quantity
        txn.date = date
        txn.save()


@receiver(Physical.Event, sender=Physical)
def physical(sender, instance, action, user, **kwargs):
    if action == Physical.REGISTER:
        stock = instance.stock
        stock.quantity += instance.delta
        stock.last_physical = instance
        stock.save()
        create_or_update_txn(stock, instance.delta, instance.date, instance)


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Stock)
def stock(sender, instance, created, **kwargs):
    logger.debug("Stock: {} {} {} created: {}".format(instance.product.name(), instance.location.name, instance.quantity, created))


#def transfer(product, quantity, origin, destination, action):
#    logger.debug("Transfer: {} qty {} from {} to {}".format(product.name(), quantity, origin.name, destination.name))
#    # do quantity updates
#    src, _ = Stock.objects.get_or_create(product=product, location=origin)
#    src.quantity -= quantity
#    src.save()
#    create_or_update_txn(src, -quantity, action.date, action)
#    dst, _ = Stock.objects.get_or_create(product=product, location=destination)
#    dst.quantity += quantity
#    dst.save()
#    create_or_update_txn(dst, quantity, action.date, action)


def update_item_account(product, user):
    item_account, _ = ItemAccount.objects.get_or_create(item_type=Product.content_type(), item_id=product.id, owner=user.account.company)
    item_account.assess()


def forward(product, quantity, origin, destination, action, user):
    src, _ = Stock.objects.get_or_create(product=product, location=origin)
    src.transact(-quantity, action)
    dst, _ = Stock.objects.get_or_create(product=product, location=destination)
    dst.transact(quantity, action)
    update_item_account(product, user)
    
    
def reverse(product, quantity, origin, destination, action, user):
    src = Stock.objects.get(product=product, location=origin)
    src.undo(action)
    dst = Stock.objects.get(product=product, location=destination)
    dst.undo(action)
    update_item_account(product, user)


@receiver(StockTransfer.Event, sender=StockTransfer)
def stock_transfer(sender, instance, action, user, **kwargs):
    if instance.labeled(StockTransfer.CANCELED):
        raise WorkflowException("Modifying a canceled document.")
    if action == StockTransfer.REGISTER or action == StockTransfer.CHECKIN:
        if action == StockTransfer.REGISTER: instance.label(StockTransfer.VALID)
        for i in instance.items.all():
            forward(i.product, i.quantity, instance.origin, instance.destination, i, user)
    elif action == StockTransfer.CHECKOUT:
        instance = StockTransfer.objects.get(pk=instance.pk)
        for i in instance.items.all():
            reverse(i.product, i.quantity, instance.origin, instance.destination, i, user)
    elif action == StockTransfer.CANCEL:
        instance.label(StockTransfer.CANCELED)
        instance.unlabel(StockTransfer.VALID)
        for i in instance.items.all():
            reverse(i.product, i.quantity, instance.origin, instance.destination, i, user)


@receiver(Adjustment.Event, sender=Adjustment)
def adjustment(sender, instance, action, user, **kwargs):
    if instance.labeled(Adjustment.CANCELED):
        raise WorkflowException("Modifying a canceled document.")
    if action == Adjustment.REGISTER or action == Adjustment.CHECKIN:
        if action == Adjustment.REGISTER: instance.label(Adjustment.VALID)
        for i in instance.items.all():
            stock = i.stock()
            stock.quantity += i.delta
            stock.save()
            create_or_update_txn(stock, i.delta, instance.date, instance)
            update_item_account(stock.product, user)
    elif action == Adjustment.CHECKOUT:
        instance = Adjustment.objects.get(pk=instance.pk)
        for i in instance.items.all():
            stock = i.stock()
            stock.quantity -= i.delta
            stock.save()
            update_item_account(stock.product, user)
    elif action == Adjustment.CANCEL:
        instance.label(Adjustment.CANCELED)
        instance.unlabel(Adjustment.VALID)
        for i in instance.items.all():
            stock = i.stock()
            stock.quantity -= i.delta
            stock.save()
            create_or_update_txn(stock, -i.delta, instance.date, instance)
            update_item_account(stock.product, user)


"""
    Trade Triggers
"""
def update_default_costs(order, user): # update default cost if it does not yet exist
    p = user.account.company
    if order.customer == p:
        for i in order.items.all():
            account = ItemAccount.objects.get(item_type=i.info_type, item_id=i.info_id, owner=p)
            if account.cost == 0:
                account.cost = i.price
            account.save()


#def snapshot(order):
#    # copy info
#    snap = OrderSnapshot()
#    stored = Order.objects.get(pk=order.pk) # get the one in the db
#    snap.date = stored.date
#    snap.code = stored.code
#    snap.source = stored
#    snap.save()
#    for label in stored.labels.all(): # copy the labels too
#        snap.label(label.name)
#    
#    # copy items
#    for item in stored.items.all():
#        item_snap = OrderItemSnapshot()
#        item_snap.order = snap
#        item_snap.price = item.price
#        item_snap.quantity = item.quantity
#        item_snap.info = item.info
#        item_snap.save()
#        for label in item.labels.all(): # copy the labels too
#            item_snap.label(label.name)

@receiver(Order.Event, sender=Order)
def order(sender, instance, action, user, **kwargs):
    if instance.labeled(Order.CANCELED):
        raise WorkflowException("Modifying a canceled document.")
    if action == Order.REGISTER:
        instance.label(Order.VALID)
        TradeAccount.objects.get_or_create(customer=instance.customer, supplier=instance.supplier)
        instance.assess()
        update_default_costs(instance, user)
    elif action == Order.CHECKOUT:
        #snapshot(instance)
        pass
    elif action == Order.CHECKIN:
        instance.assess()
        for t in instance.transfers.valid():
            if t.labeled(OrderTransfer.RETURN):
                #credit(instance.supplier, instance.customer, -t.value) # subtract            
                t.assess()
                #credit(instance.supplier, instance.customer, t.value) # add new value back
            else:
                t.assess()
                create_or_update_bill(t, user)
        update_default_costs(instance, user)
    elif action == Order.CANCEL:
        instance.label(Order.CANCELED)
        instance.unlabel(Order.VALID)
        instance.assess()
    instance.unlabel(Order.AUDITED)


def credit(supplier, customer, amount):
    account, _ = TradeAccount.objects.get_or_create(supplier=supplier, customer=customer)
    if (account.credit + amount) < 0:
        raise IntegrityError("Account credit negative.")
    account.credit += amount
    account.save()

def debit(supplier, customer, amount):
    account, _ = TradeAccount.objects.get_or_create(supplier=supplier, customer=customer)
    if (account.debt + amount) < 0:
        raise IntegrityError("Account debt negative.")
    account.debt += amount
    account.save()


@receiver(OrderTransfer.Event, sender=OrderTransfer)
def order_transfer(sender, instance, action, user, **kwargs):
    if instance.labeled(OrderTransfer.CANCELED):
        raise WorkflowException("Modifying a canceled document.")
    if action == OrderTransfer.REGISTER or action == OrderTransfer.CHECKIN:
        if action == OrderTransfer.REGISTER: 
            instance.label(OrderTransfer.VALID)
            if instance.origin.owner == instance.order.customer \
            and instance.destination.owner == instance.order.supplier:
                instance.label(OrderTransfer.RETURN)
        instance.assess()
        instance.order.assess()
        # product stock effects
        for i in instance.items.products(): # only do it for products
            forward(i.order.info, i.net_quantity, instance.origin, instance.destination, i, user)
        # produce account effects
        if instance.labeled(OrderTransfer.RETURN):
            credit(instance.order.supplier, instance.order.customer, instance.value)
        else:
            create_or_update_bill(instance, user)
    elif action == OrderTransfer.CHECKOUT:
        instance = OrderTransfer.objects.get(pk=instance.id)
        # reverse stock effects
        for i in instance.items.products(): # only do it for products
            reverse(i.order.info, i.net_quantity, instance.origin, instance.destination, i, user)
        # reverse credit effects but not bill effects
        if instance.labeled(OrderTransfer.RETURN):
            #credit(instance.order.supplier, instance.order.customer, -instance.value) # subtract
            pass
    elif action == OrderTransfer.CANCEL:
        instance.label(OrderTransfer.CANCELED)
        instance.unlabel(OrderTransfer.VALID)
        # reverse effects
        if instance.labeled(OrderTransfer.RETURN):
            #credit(instance.order.supplier, instance.order.customer, -instance.value) # subtract
            pass
        else:
            cancel_bill(instance.bill, user)
        
        for i in instance.items.products(): # only do it for products
            reverse(i.order.info, i.net_quantity, instance.origin, instance.destination, i, user)
        instance.order.assess()
    instance.order.unlabel(Order.AUDITED)


@receiver(OrderReturn.Event, sender=OrderReturn)
def order_return(sender, instance, action, user, **kwargs):
    if instance.labeled(OrderReturn.CANCELED):
        raise WorkflowException("Modifying a canceled document.")
    if action == OrderReturn.REGISTER:
        instance.label(OrderReturn.VALID)
        instance.assess()
        instance.transfer.log(OrderTransfer.CHECKOUT, user)
        instance.transfer.log(OrderTransfer.CHECKIN, user)
    elif action == OrderReturn.CANCEL:
        instance.label(OrderReturn.CANCELED)
        instance.unlabel(OrderReturn.VALID)
        instance.transfer.log(OrderTransfer.CHECKOUT, user)
        instance.transfer.log(OrderTransfer.CHECKIN, user)
    else:
        raise WorkflowException("Action not permitted")


'''
    Accounting Trigger
'''
@receiver(Payment.Event, sender=Payment)
def payment(sender, instance, action, user, **kwargs):
    if instance.labeled(Payment.CANCELED):
        raise WorkflowException("Modifying a canceled document.")
    if action == Payment.REGISTER or action == Payment.CHECKIN:
        if action == Payment.REGISTER: instance.label(Payment.VALID)
        instance.total = instance.amount - instance.refunded()  
        instance.save()
        instance.assess()
        credit(instance.supplier, instance.customer, instance.available())
    elif action == Payment.CHECKOUT:
        instance = Payment.objects.get(pk=instance.id) # the the old one
        credit(instance.supplier, instance.customer, -instance.available())
    elif action == Payment.CANCEL:
        instance.label(Payment.CANCELED)
        instance.unlabel(Payment.VALID)
        for a in instance.allocations.all():
            a.log(PaymentAllocation.ARCHIVE, user)
        instance.assess()
        credit(instance.supplier, instance.customer, -instance.available())


@receiver(Refund.Event, sender=Refund)
def refund(sender, instance, action, user, **kwargs):
    if instance.labeled(Refund.CANCELED):
        raise WorkflowException("Modifying a canceled document.")
    if action == Refund.REGISTER or action == Refund.CHECKIN:
        if action == Refund.REGISTER: instance.label(Refund.VALID)
        instance.payment.log(Payment.CHECKOUT, user)
        instance.payment.log(Payment.CHECKIN, user)
    elif action == Refund.CHECKOUT:
        pass
    elif action == Refund.CANCEL:
        instance.label(Refund.CANCELED)
        instance.unlabel(Refund.VALID)
        instance.payment.log(Payment.CHECKOUT, user)
        instance.payment.log(Payment.CHECKIN, user)


def create_or_update_bill(transfer, user):
    bill, created = Bill.objects.get_or_create(transfer=transfer, 
                                               defaults={'supplier': transfer.order.supplier, 
                                                         'customer': transfer.order.customer,
                                                         'date': transfer.date,})
    if not created:
        bill.log(Bill.CHECKOUT, user)
    bill.code = transfer.code # copy the transfer code over to the bill
    bill.amount = transfer.net_value()
    bill.save()
    if created:
        bill.log(Bill.REGISTER, user)
    else:
        bill.log(Bill.CHECKIN, user)


def undo_bill(bill, user):
    for a in bill.allocations.all():
        a.log(PaymentAllocation.ARCHIVE, user)
    debit(bill.supplier, bill.customer, -bill.total)


def cancel_bill(bill, user):
    undo_bill(bill, user)
    bill.label(Bill.CANCELED)
    bill.unlabel(Bill.VALID)
    bill.assess()


@receiver(Bill.Event, sender=Bill)
def bill(sender, instance, action, user, **kwargs):
    if instance.labeled(Bill.CANCELED):
        raise WorkflowException("Modifying a canceled document.")
    if action == Bill.REGISTER or action == Bill.CHECKIN:
        if action == Bill.REGISTER: instance.label(Bill.VALID)
        instance.total = instance.amount - instance.discount()
        instance.save()
        instance.assess()
        debit(instance.supplier, instance.customer, instance.total)
    elif action == Bill.CHECKOUT:
        instance = Bill.objects.get(pk=instance.id) # get the old one
        undo_bill(instance, user)
    elif action == Bill.CANCEL:
        if instance.transfer == None:
            cancel_bill(instance, user)
            instance.assess()
        else:
            raise WorkflowException("Canceling a transfer-based bill.")


@receiver(PaymentAllocation.Event, sender=PaymentAllocation)
def payment_allocation(sender, instance, action, user, **kwargs):
    if action == PaymentAllocation.REGISTER:
        instance.payment.assess()
        instance.bill.assess()
        account = TradeAccount.objects.get(supplier=instance.bill.supplier, customer=instance.bill.customer)
        amount = Decimal(instance.amount)
        if (account.credit - amount) < 0:
            raise IntegrityError("Account credit negative.")
        if (account.debt - amount) < 0:
            raise IntegrityError("Account debt negative.")
        account.debt -= amount
        account.credit -= amount
        account.save()
    elif action == PaymentAllocation.ARCHIVE:
        account = TradeAccount.objects.get(supplier=instance.bill.supplier, customer=instance.bill.customer)
        account.debt += instance.amount
        account.credit += instance.amount
        account.save()
        instance.delete()
        instance.payment.assess()
        instance.bill.assess()

        
@receiver(Expense.Event, sender=Expense)
def expense(sender, instance, action, user, **kwargs):
    if action == Expense.REGISTER: 
        instance.label(Expense.VALID)
    elif action == Expense.CANCEL:
        instance.label(Expense.CANCELED)
        instance.unlabel(Expense.VALID)        
    pass

