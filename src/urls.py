from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mercury.views.home', name='home'),
    # url(r'^mercury/', include('mercury.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls), name='admin'),
)


"""
    Addressbook Views
"""
urlpatterns += patterns('addressbook.views.contact',
    (r'^contacts/$', 'index'),
    (r'^contact/new/$', 'new'),
    (r'^contact/(?P<_id>\d+)/$', 'view'),
    (r'^contact/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^contact/(?P<_id>\d+)/archive/$', 'archive'),
    (r'^contact/(?P<_id>\d+)/merge/$', 'merge'),
    (r'^contact/(?P<_id>\d+)/transaction/search/$', 'transaction_search'),
    (r'^contact/(?P<_id>\d+)/transaction/search/results/$', 'transaction_search_results'),
    (r'^contact/bills/$', 'bills'),
    (r'^contact/orders/$', 'orders'),
    (r'^contact/transfers/$', 'transfers'),
    (r'^contact/payments/$', 'payments'),
    (r'^contact/expenses/$', 'expenses'),
)


"""
    Catalog Views
"""
urlpatterns += patterns('catalog.views',
    (r'^catalog/suggestions/$', 'suggestions'),
)
urlpatterns += patterns('catalog.views.product',
    (r'^product/stock/transfers/$', 'stocktransfers'),
    (r'^product/order/transfers/$', 'ordertransfers'),
    (r'^product/transactions/$', 'transactions'),
    (r'^product/suggestions/$', 'suggestions'),
    (r'^product/stocks/$', 'stocks'),
    (r'^product/(?P<_id>\d+)/$', 'view'),
    (r'^product/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^product/(?P<_id>\d+)/merge/$', 'merge'),
    (r'^product/new/$', 'new'),
)
urlpatterns += patterns('catalog.views.service',
    (r'^service/(?P<_id>\d+)/$', 'view'),
    (r'^service/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^service/new/$', 'new'),
    (r'^service/transactions/$', 'transactions'),
)


"""
    Common Views
"""
urlpatterns += patterns('common.views.search',
    (r'^search/$', 'view'),
    (r'^search/results/$', 'results'),
    (r'^search/suggestions/$', 'suggestions'),
)


"""
    Inventory Views
"""
urlpatterns += patterns('inventory.views.location',
    (r'^locations/$', 'index'),
    (r'^location/(?P<_id>\d+)/$', 'view'),
    (r'^location/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^location/new/$', 'new'),
    (r'^location/stocks/$', 'stocks'),
    (r'^location/transfers/$', 'transfers'),
    (r'^location/adjustments/$', 'adjustments'),
)
urlpatterns += patterns('inventory.views.stock',
    (r'^stock/(?P<_id>\d+)/physical/$', 'physical'),
    (r'^stock/(?P<_id>\d+)/alarms/$', 'alarms'),
    (r'^stock/transfer/$', 'transfer'),
    (r'^stock/report/$', 'report'),
)
urlpatterns += patterns('inventory.views.stocktransfer',
    (r'^stock/transfer/new/$', 'new'),
    (r'^stock/transfer/(?P<_id>\d+)/$', 'view'),
    (r'^stock/transfer/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^stock/transfer/(?P<_id>\d+)/cancel/$', 'cancel'),
    (r'^stock/transfer/item/$', 'item'),
)
urlpatterns += patterns('inventory.views.adjustment',
    (r'^location/(?P<location_id>\d+)/adjustment/$', 'new'),
    (r'^adjustment/(?P<_id>\d+)/$', 'view'),
    (r'^adjustment/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^adjustment/(?P<_id>\d+)/cancel/$', 'cancel'),
    (r'^adjustment/item/add/$', 'item'),
)


"""
    Trade Views
"""
urlpatterns += patterns('trade.views.order',
    (r'^contact/(?P<contact_id>\d+)/sale/$', 'sale'),
    (r'^contact/(?P<contact_id>\d+)/purchase/$', 'purchase'),
    (r'^order/(?P<_id>\d+)/$', 'view'),
    (r'^order/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^order/(?P<_id>\d+)/cancel/$', 'cancel'),
    (r'^order/search/$', 'search'),
#    (r'^order/snapshot/(?P<_id>\d+)/$', 'snapshot'),

    (r'^order/item/$', 'item'),
    (r'^order/item/info/$', 'item_info'),
    (r'^order/item/(?P<item_id>\d+)/transfers/$', 'item_transfers'),
    (r'^order/transfer/$', 'transfer'),
)
urlpatterns += patterns('trade.views.ordertransfer',
    (r'^order/(?P<order_id>\d+)/serve/$', 'serve'),
    (r'^order/transfer/(?P<_id>\d+)/$', 'view'),
    (r'^order/transfer/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^order/transfer/(?P<_id>\d+)/cancel/$', 'cancel'),
)
urlpatterns += patterns('trade.views.orderreturn',
    (r'^order/transfer/(?P<transfer_id>\d+)/return/$', 'new'),
    (r'^order/return/(?P<_id>\d+)/cancel/$', 'cancel'),
)
#urlpatterns += patterns('trade.views.pricelist',
#    (r'^contact/(?P<contact_id>\d+)/pricelist/$', 'edit'),
#    (r'^contact/(?P<contact_id>\d+)/pricelist/products/$', 'products'),
#    (r'^contact/(?P<contact_id>\d+)/pricelist/services/$', 'services'),
#    (r'^pricelist/price/$', 'price'),
#)


"""
    Company Views
"""
urlpatterns += patterns('company.views.trade',
    (r'^account/(?P<account_id>\d+)/edit/$', 'edit'),
)

urlpatterns += patterns('company.views.item',
    (r'^item/(?P<account_id>\d+)/price/$', 'price'),
    (r'^item/(?P<account_id>\d+)/cost/$', 'cost'),
)

"""
    Accounting Views
"""
urlpatterns += patterns('accounting.views.expense',
    (r'^expense/$', 'new'),
    (r'^expense/(?P<_id>\d+)/$', 'view'),
    (r'^expense/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^expense/(?P<_id>\d+)/cancel/$', 'cancel'),
)

urlpatterns += patterns('accounting.views.bill',
    (r'^contact/(?P<contact_id>\d+)/receivable/$', 'receivable'),
    (r'^contact/(?P<contact_id>\d+)/payable/$', 'payable'),
    (r'^contact/(?P<contact_id>\d+)/receivables/$', 'receivables'),
    (r'^contact/(?P<contact_id>\d+)/receivables/statement/$', 'receivables_statement'),
    (r'^contact/(?P<contact_id>\d+)/payables/$', 'payables'),
    (r'^contact/(?P<contact_id>\d+)/payables/statement/$', 'payables_statement'),
    (r'^bill/search/$', 'search'),
    (r'^bill/(?P<_id>\d+)/$', 'view'),
    (r'^bill/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^bill/(?P<_id>\d+)/cancel/$', 'cancel'),
    (r'^bill/(?P<_id>\d+)/quickpay/$', 'quickpay'),
    (r'^bill/(?P<_id>\d+)/toggle/writeoff/$', 'toggle_writeoff'),
)

urlpatterns += patterns('accounting.views.discount',
    (r'^bill/(?P<_id>\d+)/discount/$', 'new'),
    (r'^discount/(?P<_id>\d+)/delete/$', 'delete'),
)

urlpatterns += patterns('accounting.views.payment',
    (r'^payment/(?P<_id>\d+)/$', 'view'),
    (r'^payment/(?P<_id>\d+)/edit/$', 'edit'),
    (r'^payment/(?P<_id>\d+)/cancel/$', 'cancel'),
    (r'^contact/(?P<contact_id>\d+)/disburse/$', 'disburse'),
    (r'^contact/(?P<contact_id>\d+)/collect/$', 'collect'),
    (r'^payment/(?P<_id>\d+)/allocate/$', 'allocate'),
    (r'^payment/(?P<_id>\d+)/allocate/bills/unpaid/$', 'allocate_bills_unpaid'),
    (r'^payment/(?P<_id>\d+)/allocate/bills/allocated/$', 'allocate_bills_allocated'),
)


urlpatterns += patterns('accounting.views.refund',
    (r'^payment/(?P<_id>\d+)/refund/$', 'new'),
    (r'^refund/(?P<_id>\d+)/cancel/$', 'cancel'),
)

"""
    Task Views
"""
urlpatterns += patterns('task.views.warehousing',
    url(r'^inventory/$', 'view', name='inventory'),
    (r'^inventory/low/$', 'low'),
    (r'^inventory/negative/$', 'negative'),
    (r'^inventory/physical/$', 'for_physical'),
)

urlpatterns += patterns('task.views.sales',
    url(r'^sales/$', 'view', name='sales'),
    (r'^sales/pending/$', 'pending'),
)

urlpatterns += patterns('task.views.purchasing',
    url(r'^purchasing/$', 'view', name='purchasing'),
    (r'^purchasing/urgent/$', 'urgent'),
    (r'^purchasing/incoming/$', 'incoming'),
    (r'^purchasing/pending/$', 'pending'),
    (r'^purchasing/order/$', 'order'),
)

urlpatterns += patterns('task.views.billing',
    url(r'^accounting/$', 'view', name='accounting'),
    url(r'^accounting/bills/$', 'bills'),
    url(r'^accounting/receivables/$', 'receivables'),
    url(r'^accounting/receivables/full/$', 'receivables_full'),
    url(r'^accounting/receivables/customers/$', 'receivables_per_customer'),
    url(r'^accounting/payments/$', 'payments'),
    url(r'^accounting/expenses/$', 'expenses'),
)

urlpatterns += patterns('task.views.management',
    url(r'^management/$', 'view', name='management'),
    url(r'^management/reports/$', 'reports'),
    url(r'^management/customers/$', 'customers'),
    url(r'^management/customers/full/$', 'customers_full'),
    url(r'^management/suppliers/$', 'suppliers'),
    url(r'^management/items/$', 'items'),

    url(r'^management/costing/items/$', 'costing_items'),
    url(r'^management/costing/$', 'costing'),
    url(r'^management/sales/negative/$', 'negative_sales'),
)

urlpatterns += patterns('task.views.home',
    url(r'^$', 'view', name='home'),
)

"""
    Login Logout Views
"""
urlpatterns += patterns('',
    url(r'^login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'account/login.html'},
        name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^password/$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'account/change_password.html', 'post_change_redirect': '/'},
        name='change_password'),
)

#if settings.DEBUG:
#     urlpatterns += staticfiles_urlpatterns()
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
