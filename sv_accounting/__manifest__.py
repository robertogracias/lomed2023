# -*- coding: utf-8 -*-
{
    'name': "sv_accounting",

    'summary': """
       Agrega las posiciones fiscales e impuestos para compania salvadore;as""",

    'description': """
        Agrega una pantalla para realizar las configuraciones de impuestos
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale','sv_partner'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/documento.xml',
        'views/razon.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
