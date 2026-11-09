# -*- coding: utf-8 -*-
{
    'name': "Operaciones de transporte",

    'summary': "Gestión de vehículos, pilotos y contactos de flotilla",

    'description': """
Permite registrar vehículos y sus pilotos desde el sitio web, creando los
vehículos en flotilla y sus contactos asociados.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet', 'website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
