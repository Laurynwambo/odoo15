from odoo import models, fields, api,_


class PartnerExtension(models.Model):
    _inherit = 'res.partner'

    password = fields.Char(string="partner password")
    access_token_ids = fields.One2many(string='Access Tokens',comodel_name='jwt_provider.access_token',inverse_name='partner_id')
    otp=fields.Char(string='Otp')
    when_sent=fields.Date(string="Otp Validation")    