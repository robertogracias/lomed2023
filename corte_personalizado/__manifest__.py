# -*- coding: utf-8 -*-
{
    'name': "corte_personalizado",

    'summary': """
    Realiza el corte de caja de lomed""",

    'description': """
        Realiza el corte de caja de lomed
    """,

    'author': "RG Ingenieros S.A. De C.V.",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sv_caja'],

    # always loaded
    'data': [
        'views/views.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
