# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class FleetVehicleRequestController(http.Controller):

    @http.route(
        '/flotilla/solicitud',
        type='http',
        auth='public',
        website=True,
        methods=['GET', 'POST'],
        sitemap=True,
    )
    def fleet_vehicle_request(self, **post):
        vehicle_models = request.env['fleet.vehicle.model'].sudo().search([
            ('active', '=', True),
        ])
        form_values = {
            'vehicle_model_id': post.get('vehicle_model_id', ''),
            'license_plate': post.get('license_plate', ''),
            'contact_name': post.get('contact_name', ''),
            'phone': post.get('phone', ''),
            'email': post.get('email', ''),
        }
        error = False

        if request.httprequest.method == 'POST':
            model_id = 0
            try:
                model_id = int(form_values['vehicle_model_id'])
            except (TypeError, ValueError):
                error = 'Selecciona un modelo válido.'

            vehicle_model = request.env['fleet.vehicle.model'].sudo().search([
                ('id', '=', model_id),
                ('active', '=', True),
            ], limit=1)
            if not vehicle_model:
                error = 'Selecciona un modelo válido.'
            elif not form_values['license_plate'].strip():
                error = 'Ingresa la matrícula del vehículo.'
            elif not form_values['contact_name'].strip():
                error = 'Ingresa tu nombre.'
            elif not form_values['phone'].strip():
                error = 'Ingresa tu número de teléfono.'

            if not error:
                request.env['fleet.vehicle.request'].sudo().create({
                    'name': '%s - %s' % (
                        vehicle_model.display_name,
                        form_values['license_plate'].strip(),
                    ),
                    'vehicle_model_id': vehicle_model.id,
                    'license_plate': form_values['license_plate'].strip(),
                    'contact_name': form_values['contact_name'].strip(),
                    'phone': form_values['phone'].strip(),
                    'email': form_values['email'].strip(),
                })
                return request.redirect('/flotilla/solicitud?success=1')

        return request.render('l10n_gt_chuminos.fleet_vehicle_request_page', {
            'error': error,
            'success': post.get('success') == '1',
            'vehicle_models': vehicle_models,
            'form_values': form_values,
        })
