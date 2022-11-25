from odoo import api,_, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_round, float_repr, float_compare
from odoo.http import request, Response
from datetime import datetime
import xmlrpc.client
import logging
import json

_logger = logging.getLogger(__name__)

today= datetime.today().strftime('%Y-%m-%d')
STATE = [
    ('draft', 'Draft'),
    ('confirm', 'Confirmed')
]

class DbConnection(models.Model):
    _name = 'db.connection'
    _description = 'Database connections'

    user_id=fields.Many2one('res.users',string='System User')
    password=fields.Char(string='Password')
    state = fields.Selection(selection=STATE, string="Connection State",default='draft',readonly=True)

    def cancel_db_connection(self):
        if self.state == 'confirm':
            self.sudo().write({'state':'draft','password':'1W3^Ns47$3si'})
            return{
                'type':'ir.actions.client',
                'tag':'display_notification',
                'params':{
                    'message':'You have Cancelled the connections',
                    'title': _("DB CONNECTION CANCELLATION"),
                    'type':'warning',
                    'sticky':False
                }
              }
    def check_db_connection(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        db=self.pool.db_name
        username = self.user_id.login
        password=self.password
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.authenticate(db, username, password, {})
        successMessage='Connection was Successfuly'
        errorMessage='Wrong Database Credentials'
        if uid:
            self.sudo().write({'state':'confirm'})
            return{
                'type':'ir.actions.client',
                'tag':'display_notification',
                'params':{
                    'message':successMessage,
                    'title': _("DB CONNECTION CONFIRMATION"),
                    'type':'success',
                    'sticky':False
                }
              }
        else:
            return{
                'type':'ir.actions.client',
                'tag':'display_notification',
                'params':{
                    'message':errorMessage,
                    'title': _("DB CONNECTION ERROR"),
                    'type':'warning',
                    'sticky':True
                }
              }