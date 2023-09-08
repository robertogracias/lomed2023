# -*- coding: utf-8 -*-

{
    'name': 'Single Invoice for Multiple Sale Orders',
    'category': 'Accounting/Accounting',
    'version': '16.0',
    'author': 'SprintERP',
    'website': 'http://www.sprinterp.com',
    'summary': """You can use this application to combine several sales orders from the same customer into a single invoice.""",
    'description': """
        You can use this application to combine several sales orders from the same customer into a single invoice.
    """,
    'depends': ['sale_management', 'account'],
    'data': [
        'views/account_invoice_views.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'application': True,
    'installable': True,
    'price': 15,
	'currency': 'EUR',
}
