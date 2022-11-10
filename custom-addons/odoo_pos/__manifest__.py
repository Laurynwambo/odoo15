# -*- coding: utf-8 -*-
{
    'name': "odoo_pos",
    'summary': """Summary Odoo POS inherit from JS""",
    'description': """ Odoo POS Order""",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
