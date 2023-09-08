# -*- coding: utf-8 -*-
{
    'name': "lomed",

    'summary': """
       Personalizaciones especificas para LOMED""",

    'description': """
       Personalizaciones especificas para LOMED
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp','barcodes','sale'],

    # always loaded
    'data': [
        'views/views.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'lomed/static/src/js/barcode.js',
            'lomed/static/src/js/BrowserPrint-3.0.216.min.js',
            'lomed/static/src/js/BrowserPrint-Zebra-1.0.216.min.js',
        ],       
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
