from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_round, float_repr, float_compare
from odoo.http import request, Response
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)

today= datetime.today().strftime('%Y-%m-%d')
class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Description'

class PosOrder(models.Model):
    _inherit = 'pos.order'
    _description = 'Description'

    @api.model
    def create_from_ui(self, orders, draft=False):
        context = self._context
        current_uid = context.get('uid')
        logged_in_user = self.env['res.users'].browse(current_uid)
        data=orders[0]["data"]
        payload=data['lines']
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        the_id=[o['id'] for o in order_ids]
        the_order = request.env['pos.order'].sudo().search([('id','=',the_id)])
        # for check_status in the_order.lines:
        #     if check_status.product_id.
        if the_order:
            laundry_values={
            "partner_id":the_order.partner_id.id,
            "order_date":the_order['date_order'],
            "partner_invoice_id":the_order.partner_id.id,
            "partner_shipping_id":the_order.partner_id.id,
            "laundry_person":the_order['user_id'].id  
            }
        laundry_order = request.env['laundry.order'].sudo().create(laundry_values)
        for rec in payload:
            record=rec[2]['washing_stage'].lower()
            work_id = request.env['washing.type'].sudo().search([(('name'.lower()),'=',record)])
            if work_id:
                laundry_lines={
                'product_id':rec[2]['product_id'],
                'amount':work_id.amount,
                'washing_type':work_id.id,
                'laundry_obj':laundry_order.id,
                'description':rec[2]['description'],
                'qty':rec[2]['qty']
                }
                order_lines = request.env['laundry.order.line'].sudo().create(laundry_lines)
            else:
                data={
                     "name":rec[2]['washing_stage'].lower(),
                    "amount":rec[2]['washing_amount'],
                    "assigned_person":logged_in_user.id
                }
                work_id = request.env['washing.type'].sudo().create(data)
                laundry_lines={
                'product_id':rec[2]['product_id'],
                'amount':work_id.amount,
                'washing_type':work_id.id,
                'laundry_obj':laundry_order.id,
                'description':rec[2]['description'],
                'qty':rec[2]['qty']
                }
                order_lines = request.env['laundry.order.line'].sudo().create(laundry_lines)
        for order in self.sudo().browse([o['id'] for o in order_ids]):
            for line in order.lines.filtered(lambda l: l.product_id == order.config_id.down_payment_product_id and l.qty > 0 and l.sale_order_origin_id):
                sale_lines = line.sale_order_origin_id.order_line
                sale_line = self.env['sale.order.line'].create({
                    'order_id': line.sale_order_origin_id.id,
                    'product_id': line.product_id.id,
                    'price_unit': line.price_unit,
                    'product_uom_qty': 0,
                    'tax_id': [(6, 0, line.tax_ids.ids)],
                    'is_downpayment': True,
                    'discount': line.discount,
                    'sequence': sale_lines and sale_lines[-1].sequence + 1 or 10,
                })
                sale_line._compute_tax_id()
                line.sale_order_line_id = sale_line

            so_lines = order.lines.mapped('sale_order_line_id')

            # confirm the unconfirmed sale orders that are linked to the sale order lines
            sale_orders = so_lines.mapped('order_id')
            _logger.error(order_ids)
            for sale_order in sale_orders.filtered(lambda so: so.state in ['draft', 'sent']):
                sale_order.action_confirm()

            # update the demand qty in the stock moves related to the sale order line
            # flush the qty_delivered to make sure the updated qty_delivered is used when
            # updating the demand value
            so_lines.flush(['qty_delivered'])
            # track the waiting pickings
            waiting_picking_ids = set()
            for so_line in so_lines:
                for stock_move in so_line.move_ids:
                    picking = stock_move.picking_id
                    if not picking.state in ['waiting', 'confirmed', 'assigned']:
                        continue
                    new_qty = so_line.product_uom_qty - so_line.qty_delivered
                    if float_compare(new_qty, 0, precision_rounding=stock_move.product_uom.rounding) <= 0:
                        new_qty = 0
                    stock_move.product_uom_qty = so_line.product_uom._compute_quantity(new_qty, stock_move.product_uom, False)
                    waiting_picking_ids.add(picking.id)

            def is_product_uom_qty_zero(move):
                return float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding)

            # cancel the waiting pickings if each product_uom_qty of move is zero
            for picking in self.env['stock.picking'].browse(waiting_picking_ids):
                if all(is_product_uom_qty_zero(move) for move in picking.move_lines):
                    picking.action_cancel()

        return order_ids



class ProductProduct(models.Model):
    _inherit = "product.product"
    _description = "product inherit lines"
    # _rec_name = "product_id"


    service_type = fields.Selection([
        ('l_service', 'Laundry Service'),
        ('other_service', 'Other Serviice')],
        string='Type of Service')