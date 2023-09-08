# -*- coding: utf-8 -*-
{
    'name': "sv_electronica",

    'summary': """
       Contiene las configuraciones para la facturacion electronica de El Salvador""",

    'description': """
        Contiene las configuraciones para la facturacion electronica de El Salvador
    """,

    'author': "RG Ingenieros",
    'website': "https://rgingenierossv.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sv_accounting'],

    # always loaded
    'data': [
        'data/data.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
