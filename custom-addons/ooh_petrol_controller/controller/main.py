# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from datetime import date
import math
import json
import logging

_logger = logging.getLogger(__name__)
today = date.today()


class Products(http.Controller):
    @http.route('/get_products', type='json', auth='public', cors='*')
    def get_products(self, **kwargs):
        data = json.loads(request.httprequest.data)
        base_url = request.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        products = []
        total = 0.00
        products_rec = request.env['product.product'].sudo().search(
            [('on_app', '=', True)])
        readings = request.env['fuels.stock'].sudo().search(
            [('state', '=', 'approved'), ('salesperson.login', '=', data['email'])])
        for rec in readings:
            total += rec.sold
        for rec in products_rec:
            url = f"""{base_url}/web/image/product.product/{rec.id}/image_1920"""
            vals = {
                'id': rec.id,
                'name': rec.name,
                'qty': rec.qty_available,
                'image': url,
                'price': rec.list_price
            }
            products.append(vals)
        data = {
            'code': 200,
            'sales': total,
            'products': products,
            'success': True,
            'message': 'Success',
        }
        return data

    @http.route('/get_today_sales', type='json', auth='public', cors='*')
    def get_sales_today_per_person(self, email=None):
        data = json.loads(request.httprequest.data)
        totalSales = 0.00
        todaySales = []
        if not data['email']:
            return {
                'code': 400,
                'message': 'Email address not provided'
            }
        user = request.env['res.users'].sudo().search(
            [('login', '=', data['email'])])
        domain = [('date', '=', today), ('salesperson.login', '=', user.id)]
        sales_rec = request.env['account.payment'].sudo().search(domain)
        for res in sales_rec:
            totalSales += res.amount
            vals = {
                'id': res.id,
                'ref': res.ref,
                'amt': res.amount
            }
            todaySales.append(vals)
            return {
                'code': 200,
                'status': 'Success',
                'totalSales': totalSales,
                'sales': todaySales if len(todaySales) > 0 else [],
                'message': 'These are the availeble products' if len(todaySales) > 0 else 'There are no products',
            }

    @http.route('/get_sales_per_person', type='json', auth='public', cors='*')
    def get_sales_per_person(self, email=None):
        data = json.loads(request.httprequest.data)
        sales = []
        weeklySales = 0.00
        if not data['email']:
            return {
                'code': 400,
                'message': 'Email address not provided'
            }
        domain = [('invoice_user_id.login', '=', data['email']),
                  ('payment_state', 'in', ['paid'])]
        inv = request.env['account.move'].sudo().search(domain)
        user = request.env['res.users'].sudo().search(
            [('login', '=', data['email'])]).has_group('sales_team.group_sale_manager')
        readings = request.env['fuels.stock'].sudo().search(
            [('state', '=', 'draft')])
        if user:
            for res in readings:
                if res.date.isocalendar().week == today.isocalendar().week:
                    weeklySales += res.sales
                vals = {
                    'id': res.id,
                    'name': res.product_name.name,
                    'amt': res.sales,
                    'units': res.sold,
                    'salesp': res.salesperson.name,
                    'status': res.state,
                    'date': res.date
                }
                sales.append(vals)
            return {
                'code': 200,
                'status': 'Success',
                'weekSale': math.trunc(weeklySales),
                'fPart': int(weeklySales-math.trunc(weeklySales)),
                'sales': sales,
                'message': 'These are sales for the email' if len(sales) > 0 else 'There are no products',
            }
        else:
            for rec in inv:
                if rec.invoice_date.isocalendar().week == today.isocalendar().week:
                    weeklySales += rec.amount_total
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    # 'amt':round(rec.invoice_line_ids[0].product_id.list_price*rec.invoice_line_ids[0].quantity,2),
                    'amt': rec.amount_total,
                    'units': 0.00,
                    'date': rec.invoice_date
                }
                sales.append(vals)
            return {
                'code': 200,
                'status': 'Success',
                'weekSale': math.trunc(weeklySales),
                'fPart': int(weeklySales-math.trunc(weeklySales)),
                'sales': sales,
                'message': 'These are sales for the email' if len(sales) > 0 else 'There are no products',
            }

    def _prepare_payment_values(self, item):
        _logger.error(item)
        _logger.error('THE INVOICE ID VALUES!!!')
        # customer = request.env['res.partner'].with_user(item.salesperson.id).search([('name','ilike','Direct Sales Customer')])
        # journal = request.env['account.journal'].with_user(item.salesperson.id).search([('code','ilike','DRSC')])
        payment_journal = request.env['account.journal'].with_user(
            item.invoice_user_id.id).search([('type', '=', ['bank', 'cash'])])
        invoice_id = request.env['account.move'].with_user(
            item.invoice_user_id.id).search([('id', '=', item.id)])
        # account = request.env['ir.config_parameter'].sudo().get_param('account.account_journal_payment_credit_account_id')
        ctx = {'active_model': 'account.move', 'active_ids': item.id}
        payment_register = request.env['account.payment.register'].with_context(**ctx).with_user(item.invoice_user_id.id).create({
            'amount': invoice_id.amount_residual,
            'journal_id': payment_journal[0].id,
            'payment_date': today,
            'company_id':invoice_id.company_id.id,
            'communication': invoice_id.name,
        })
        payment_register.action_create_payments()
        return payment_register

    def _prepare_invoice_values(self, item):
        customer = request.env['res.partner'].with_user(item.salesperson.id).search(
            [('name', 'ilike', 'Direct Sales Customer')])
        journal = request.env['account.journal'].with_user(
            item.salesperson.id).search([('code', 'ilike', 'DRSC')])
        payment_journal = request.env['account.journal'].with_user(
            item.salesperson.id).search([('type', '=', ['bank', 'cash'])])
        # account = request.env['ir.config_parameter'].sudo().get_param('account.account_journal_payment_credit_account_id')
        sale_order = request.env['sale.order'].sudo().create({
            'partner_id': customer.id,
            'date_order': today,
            'validity_date': today,
            'user_id': item.salesperson.id,
            'payment_term_id': 1,
            'order_line': [(0, 0, {
                'product_id': item.product_name.id,
                'name': item.product_name.name,
                'price_unit': item.price,
                'price_subtotal': item.sales,
                'product_uom_qty': item.sold,
            })]
        })
        if sale_order:
            sale_order.action_confirm()
            context = {
                "active_model": 'sale.order',
                "active_ids": [sale_order.id],
                "active_id": sale_order.id,
                'open_invoices': True,
            }
            # Invoice the 1
            wizard = request.env['sale.advance.payment.inv'].with_context(context).with_user(
                item.salesperson.id).create({'advance_payment_method': 'delivered'})
            invoice_dict = wizard.create_invoices()
            # Confirm the invoice
            invoice = request.env['account.move'].with_user(
                item.salesperson.id).browse(invoice_dict['res_id'])
            invoice.action_post()
            return invoice
            # if invoice:
            #     payment = self._prepare_payment_values(invoice)

    @http.route('/confirm_reading', type='json', auth='public', cors='*')
    def confirm_reading(self, **kwargs):
        data = json.loads(request.httprequest.data)
        payment=0
        if not data['email']:
            return {
                'code': 400,
                'message': 'Email Cannot Be Empty'
            }
        if not data['reading_id']:
            return {
                'code': 400,
                'message': 'Reading Cannot Be Empty'
            }
        user = request.env['res.users'].sudo().search(
            [('login', '=', data['email'])])
        reading_id = request.env['fuels.stock'].with_user(
            user.id).search([('id', '=', data['reading_id'])])
        product_id = request.env['product.product'].with_user(
            user.id).search([('id', '=', reading_id.product_name.id)])
        product_template_id = request.env['product.template'].with_user(
            user.id).search([('name', '=', product_id.name)])
        if reading_id:
            warehouse = request.env['stock.warehouse'].with_user(user.id).search(
                [('company_id', '=', request.env.company.id)], limit=1)
            item = request.env['stock.change.product.qty'].with_user(user.id).create({
                'product_id': reading_id.product_name.id,
                'product_tmpl_id': product_template_id.id,
                'new_quantity': reading_id.stop,
            })
            request.env['stock.quant'].with_context(inventory_mode=True).with_user(user.id).create({
                'product_id': item.product_id.id,
                'location_id': warehouse.lot_stock_id.id,
                'inventory_quantity': item.new_quantity})._apply_inventory()
            reading_id.with_user(user.id).write({'state': 'approved'})
            invoice_id = self._prepare_invoice_values(reading_id)
            if invoice_id:
                payment = self._prepare_payment_values(invoice_id)
            return {
                "code": 200,
                "invoice": invoice_id.id,
                "payment": "You have SUccessfuly Created an Invoice" if payment.id >0 else "You did not create any Payment for the Invoice",
                "record": reading_id.product_name.qty_available,
                "message": 'You have confirmed the pump reading'
            }

    @http.route('/closing_stock', type='json', auth='public', cors='*')
    def close_stock(self, **kwargs):
        data = json.loads(request.httprequest.data)
        if not data['product_id']:
            return {
                'code': 400,
                'message': 'Product Cannot be Empty'
            }
        if not data['reading']:
            return {
                'code': 400,
                'message': 'Stop Reading Cannot Be Empty'
            }

        if not data['email']:
            return {
                'code': 400,
                'message': 'Email Cannot Be Empty'
            }
        user_id = request.env['res.users'].sudo().search(
            [('login', '=', data['email'])])
        product_id = request.env['product.product'].with_user(
            user_id.id).search([('id', '=', data['product_id'])])
        if int(data['reading']) > product_id.qty_available:
            return {
                "code": 200,
                "message": 'Reading Cannot be greater than Available quantity'
            }

        else:
            cost = (product_id.qty_available -
                    int(data['reading']))*product_id.list_price
            new_record = request.env['fuels.stock'].with_user(user_id.id).create({
                'product_name': product_id.id,
                'price': product_id.list_price,
                'start': product_id.qty_available,
                'stop': int(data['reading']),
                'date': today,
                'salesperson': user_id.id,
                'sales': cost
            })
            return {
                "code": 200,
                "record": new_record.id,
                "message": 'Successfully created a record'
            }
