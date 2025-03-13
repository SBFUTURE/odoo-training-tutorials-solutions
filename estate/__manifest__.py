# -*- coding: utf-8 -*-
{
    'name': 'Estate',
    'version': '1.0',
    'summary': 'Real Estate Management',
    'description': 'Manage real estate properties, sales, and leases.',
    'category': 'Sales',
    'author': 'Your Name',
    'website': 'http://www.yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer.xml',
        'views/view_users.xml',
    ],
    'installable': True,
    'application': True,
}