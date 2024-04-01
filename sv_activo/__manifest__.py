# -*- coding: utf-8 -*-
{
    'name': "sv_activo",

    'summary': """
       Contiene adiciones a los activos fijos para El Salvador""",

    'description': """
        Contiene adiciones a los activos fijos para El Salvador
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account_asset'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/categoria.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
