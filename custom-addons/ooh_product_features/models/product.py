from odoo import models, fields, api,_


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    qty_available=fields.Float(related='product_id.virtual_available',string="Available")