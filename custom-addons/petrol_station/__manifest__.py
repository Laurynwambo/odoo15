# -*- coding: utf-8 -*-
{
    'name': "petrol_station",

    'summary': """
        Petrol Station Management System""",

    'description': """
        System used for managing a petrol station
    """,

    'author': "My Company",
    'website': "http://www.petrolstation.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',
    'sequence': 5,
    'installable': True,
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_expense','hr_attendance', 'hr_contract','sale','mail','contacts','product', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/fuel.xml',
        'views/product.xml',
         'views/sequence.xml',
        'views/vehicles.xml',
        'views/services.xml',
        # 'views/stock_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
