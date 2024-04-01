# -*- coding: utf-8 -*-
{
    'name': "sv_ruta",

    'summary': """
       Agregar los datos requeridos por hmt""",

    'description': """
        Agrega los datos requeridos por hmt
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale_management'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/ruta.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
