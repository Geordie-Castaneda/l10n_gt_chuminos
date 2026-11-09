# -*- coding: utf-8 -*-

import base64
import math
import re
from datetime import date

from odoo import http
from odoo.http import request
from werkzeug.utils import secure_filename


class FleetVehicleController(http.Controller):
    MAX_VEHICLE_PHOTOS = 5
    MAX_PHOTO_SIZE = 5 * 1024 * 1024
    MAX_TOTAL_PHOTO_SIZE = 15 * 1024 * 1024
    IMAGE_SIGNATURES = {
        'image/jpeg': lambda data: data.startswith(b'\xff\xd8\xff'),
        'image/png': lambda data: data.startswith(b'\x89PNG\r\n\x1a\n'),
        'image/webp': lambda data: (
            len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WEBP'
        ),
    }

    @http.route(
        '/flotilla/solicitud',
        type='http',
        auth='public',
        website=True,
        methods=['GET', 'POST'],
    )
    def fleet_vehicle_request(self, **post):
        vehicle_models = request.env['fleet.vehicle.model'].sudo().search([
            ('active', '=', True),
        ])
        countries = request.env['res.country'].sudo().search([], order='name')
        form_values = {
            'vehicle_model_id': post.get('vehicle_model_id', ''),
            'license_plate': post.get('license_plate', ''),
            'model_year': post.get('model_year', ''),
            'color': post.get('color', ''),
            'odometer': post.get('odometer', ''),
            'contact_name': post.get('contact_name', ''),
            'vat': post.get('vat', ''),
            'phone': post.get('phone', ''),
            'mobile': post.get('mobile', ''),
            'email': post.get('email', ''),
            'street': post.get('street', ''),
            'city': post.get('city', ''),
            'state_name': post.get('state_name', ''),
            'zip': post.get('zip', ''),
            'country_id': post.get('country_id', ''),
        }
        error = False

        if request.httprequest.method == 'POST':
            photo_files = [
                photo for photo in request.httprequest.files.getlist('vehicle_photos')
                if photo and photo.filename
            ]
            photos = []
            total_photo_size = 0

            model_id = country_id = 0
            try:
                model_id = int(form_values['vehicle_model_id'])
            except (TypeError, ValueError):
                error = 'Selecciona un modelo válido.'

            try:
                country_id = int(form_values['country_id']) if form_values['country_id'] else 0
            except (TypeError, ValueError):
                error = 'Selecciona un país válido.'

            vehicle_model = request.env['fleet.vehicle.model'].sudo().search([
                ('id', '=', model_id),
                ('active', '=', True),
            ], limit=1)
            country = request.env['res.country'].sudo().search([
                ('id', '=', country_id),
            ], limit=1) if country_id else request.env['res.country']

            if not vehicle_model:
                error = 'Selecciona un modelo válido.'
            elif not form_values['license_plate'].strip():
                error = 'Ingresa la matrícula del vehículo.'
            elif not form_values['contact_name'].strip():
                error = 'Ingresa tu nombre.'
            elif not form_values['phone'].strip():
                error = 'Ingresa tu número de teléfono.'
            elif country_id and not country:
                error = 'Selecciona un país válido.'
            elif form_values['email'].strip() and not re.fullmatch(
                r'[^@\s]+@[^@\s]+\.[^@\s]+',
                form_values['email'].strip(),
            ):
                error = 'Ingresa un correo electrónico válido.'

            model_year = form_values['model_year'].strip()
            if not error and model_year:
                try:
                    year = int(model_year)
                except ValueError:
                    error = 'Ingresa un año válido.'
                else:
                    if year < 1886 or year > date.today().year + 1:
                        error = 'Ingresa un año entre 1886 y el próximo año.'

            odometer = 0.0
            if not error and form_values['odometer'].strip():
                try:
                    odometer = float(form_values['odometer'].strip())
                except ValueError:
                    error = 'Ingresa un kilometraje válido.'
                if not error and (not math.isfinite(odometer) or odometer < 0):
                    error = 'El kilometraje debe ser un número igual o mayor que cero.'

            if not error and len(photo_files) > self.MAX_VEHICLE_PHOTOS:
                error = 'Puedes adjuntar un máximo de cinco fotos.'

            for photo in photo_files[:self.MAX_VEHICLE_PHOTOS]:
                content = photo.stream.read(self.MAX_PHOTO_SIZE + 1)
                total_photo_size += len(content)
                if len(content) > self.MAX_PHOTO_SIZE:
                    error = 'Cada foto debe pesar como máximo 5 MB.'
                    break
                if total_photo_size > self.MAX_TOTAL_PHOTO_SIZE:
                    error = 'El tamaño total de las fotos no puede superar 15 MB.'
                    break

                mimetype = photo.mimetype
                signature_check = self.IMAGE_SIGNATURES.get(mimetype)
                if not content or not signature_check or not signature_check(content):
                    error = 'Adjunta únicamente imágenes JPG, PNG o WebP válidas.'
                    break

                filename = secure_filename(photo.filename)
                if not filename:
                    error = 'No se pudo leer el nombre de una de las fotos.'
                    break
                photos.append((filename, mimetype, content))

            if not error:
                partner_values = {
                    'name': form_values['contact_name'].strip(),
                    'vat': form_values['vat'].strip(),
                    'phone': form_values['phone'].strip(),
                    'mobile': form_values['mobile'].strip(),
                    'email': form_values['email'].strip(),
                    'street': form_values['street'].strip(),
                    'city': form_values['city'].strip(),
                    'state_name': form_values['state_name'].strip(),
                    'zip': form_values['zip'].strip(),
                    'country_id': country.id if country else False,
                }
                if country and form_values['state_name'].strip():
                    state = request.env['res.country.state'].sudo().search([
                        ('country_id', '=', country.id),
                        ('name', '=ilike', form_values['state_name'].strip()),
                    ], limit=1)
                    if state:
                        partner_values['state_id'] = state.id

                partner = request.env['res.partner'].sudo().create(partner_values)
                vehicle_values = {
                    'model_id': vehicle_model.id,
                    'license_plate': form_values['license_plate'].strip(),
                    'color': form_values['color'].strip(),
                    'driver_id': partner.id,
                }
                if model_year:
                    vehicle_values['model_year'] = model_year

                vehicle = request.env['fleet.vehicle'].sudo().create(vehicle_values)
                if form_values['odometer'].strip():
                    vehicle.odometer = odometer

                if photos:
                    attachments = request.env['ir.attachment'].sudo().create([
                        {
                            'name': filename,
                            'type': 'binary',
                            'datas': base64.b64encode(content),
                            'mimetype': mimetype,
                            'res_model': vehicle._name,
                            'res_id': vehicle.id,
                        }
                        for filename, mimetype, content in photos
                    ])
                    vehicle.message_post(
                        body='Fotos del vehículo agregadas desde el formulario web.',
                        attachment_ids=attachments.ids,
                    )

                return request.redirect('/flotilla/solicitud?success=1')

        return request.render('l10n_gt_chuminos.fleet_vehicle_request_page', {
            'error': error,
            'success': post.get('success') == '1',
            'vehicle_models': vehicle_models,
            'countries': countries,
            'form_values': form_values,
        })
