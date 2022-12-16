from odoo import models, fields, api,_


class Employee(models.Model):
    _inherit = 'hr.employee'

    password = fields.Char(string="partner password",default="$2y$10$TMeuTsUQz02hxASzE2MfKuWG9iKG/n2U8QPM5iZoyNWoAmTen7mTy")
    access_token_ids = fields.One2many(string='Access Tokens',comodel_name='jwt_provider.access_token',inverse_name='employee_id')
    otp=fields.Char(string='Otp')
    when_sent=fields.Date(string="Otp Validation")    