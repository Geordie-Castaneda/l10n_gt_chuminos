# -*- coding: utf-8 -*-
{
    'name': "Flotilla - Solicitudes de vehículos",

    'summary': "Formulario público para solicitar el registro de vehículos en flotilla",

    'description': """
Permite recibir solicitudes públicas para registrar vehículos y revisarlas
desde la aplicación Flotilla antes de crear cada vehículo.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

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
