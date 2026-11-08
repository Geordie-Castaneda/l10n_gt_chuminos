# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.exceptions import UserError


class FleetVehicleRequest(models.Model):
    _name = 'fleet.vehicle.request'
    _description = 'Solicitud de vehículo para flotilla'
    _order = 'create_date desc'

    name = fields.Char(required=True, default=lambda self: _('Nueva solicitud de flotilla'))
    vehicle_model_id = fields.Many2one(
        'fleet.vehicle.model',
        string='Modelo del vehículo',
        required=True,
        ondelete='restrict',
    )
    license_plate = fields.Char(string='Matrícula', required=True)
    contact_name = fields.Char(string='Nombre de contacto', required=True)
    phone = fields.Char(string='Teléfono', required=True)
    email = fields.Char(string='Correo electrónico')
    state = fields.Selection(
        [
            ('pending', 'Pendiente de revisión'),
            ('approved', 'Aprobada'),
            ('rejected', 'Rechazada'),
        ],
        string='Estado',
        default='pending',
        required=True,
        readonly=True,
    )
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehículo creado', readonly=True, copy=False)

    def action_approve(self):
        for vehicle_request in self:
            if vehicle_request.state != 'pending':
                raise UserError(_('Solo se pueden aprobar solicitudes pendientes.'))

            vehicle = self.env['fleet.vehicle'].create({
                'model_id': vehicle_request.vehicle_model_id.id,
                'license_plate': vehicle_request.license_plate,
            })
            vehicle_request.write({
                'state': 'approved',
                'vehicle_id': vehicle.id,
            })

    def action_reject(self):
        for vehicle_request in self:
            if vehicle_request.state != 'pending':
                raise UserError(_('Solo se pueden rechazar solicitudes pendientes.'))
            vehicle_request.state = 'rejected'
