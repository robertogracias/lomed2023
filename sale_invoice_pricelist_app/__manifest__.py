# -*- coding: utf-8 -*-

{
    'name' : 'Sales and Invoice Pricelist',
    'author': "Edge Technologies",
    'version' : '16.0.1.0',
    'live_test_url':'https://youtu.be/9emykmSof6A',
    "images":["static/description/main_screenshot.png"],
    'summary' : 'Account invoice pricelist vendor bill pricelist apply pricelist on invoice update values on pricelist change on sales pricelist easy to update order line from pricelist on account invoice price-list select pricelist on invoice',
    'description' : """
        Sale and account invoice pricelist
    """,
    'depends' : ['account','sale_management'],
    "license" : "OPL-1",
    'data': [
        # 'views/inherit_sale_order.xml',
        'views/inherit_account_invoice.xml',
            ],
    'qweb' : [],
    'demo' : [],
    'installable' : True,
    'auto_install' : False,
    'price': 22,
    'currency': "EUR",
    'category' : 'Sales',
}
