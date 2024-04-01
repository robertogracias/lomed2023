# -*- coding: utf-8 -*-
{
    'name': "sv_reports_iva",

    'summary': """Reportes de IVA en el Salvador""",

    'description': "Reportes de IVA en el Salvador",

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Reporting',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sv_accounting','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_report.xml',
        'views/taxpayer_report.xml',
        'views/consumer_report.xml',
        #'views/ticket_report_pdf_view.xml',
        #'wizard/wizard_purchases_report.xml',
        #'wizard/wizard_taxpayer_sales_report.xml',
        #'wizard/wizard_consumer_report.xml',
        'views/calculo.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'instalable': True,
    'auto_install': False,
}
