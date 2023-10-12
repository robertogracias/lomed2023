# -*- coding: utf-8 -*-
{
    'name': "ECharts Widget",
    'summary': 'ECharts widget for odoo form view.',
    'description': """
        Use eCharts to display various charts such as line charts, bar charts, pie charts, etc. on Odoo's Form view, support all chart types of echarts
    """,
    'author': "SHANGHAI YUM TOWN FOOD CO., LTD.",
    'website': "https://www.yumtown.cn",
    'support': 'it@yumtown.com.cn',
    'category': 'base',
    'version': '2.0',
    'depends': ['base', 'web'],
   'assets': {
        'web.assets_backend': [
            'echarts_widget/static/src/**/*',
        ],
    },
    'images': ['static/description/images/screenshot.png', 'static/description/images/screenshot1.png'],
    'license': 'OPL-1',
    'price': 49,
    'currency': 'USD',
}
