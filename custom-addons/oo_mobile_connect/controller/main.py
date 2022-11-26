from odoo import http
from odoo.http import request, Response
import logging
import json

_logger = logging.getLogger(__name__)


class MobileConnect(http.Controller):
    @http.route('/api/invoices', type='json', auth='public', cors='*', method=['POST'])
    def get_invoices(self, email=None):
        invoices = []
        invoice_paid_amount = 0.00
        paid = 0.00
        not_paid = 0.00
        data = json.loads(request.httprequest.data)
        if not data['email']:
            response = {
                'code': 400,
                'message': 'Email address not provided'
            }
            return response
        invoice = request.env['account.move'].sudo().search([
            ("payment_reference", "ilike", "INV"),
            ('state', '=', 'posted'),
            ('partner_id.email', '=', data['email'])
        ])
        for rec in invoice:
            for line in rec._get_reconciled_info_JSON_values():
                invoice_paid_amount += line['amount']
                paid += line['amount']
            not_paid += rec.amount_residual
            inv_info = {
                "ref": rec.name,
                "inv_date": rec.invoice_date,
                "due_date": rec.invoice_date_due,
                "due_amount": round(rec.amount_residual, 2),
                "inv_status": rec.payment_state,
                "paid_amount": round(invoice_paid_amount, 2)
            }
            invoices.append(inv_info)
        return {
            "status": 200,
            'response': invoices,
            'paid': round(paid, 3),
            'items': len(invoice),
            'not_paid': round(not_paid, 3),
            'percentage': round(not_paid / (not_paid + paid) * 100, 2) if not_paid > 0 else 0.00,
            "message": "Invoices for the Provided Email"
        }

    @http.route('/api/payments', type='json', auth='public', cors='*', method=['POST'])
    def get_payments(self, email=None):
        payments = []
        paid = 0.00
        data = json.loads(request.httprequest.data)
        if not data['email']:
            response = {
                'code': 400,
                'message': 'Email address not provided'
            }
            return response
        payment = request.env['account.payment'].sudo().search([
            ('partner_id.email', '=', data['email']),
            ('payment_type', '=', 'inbound')
        ])
        for rec in payment:
            paid += round(rec.amount, 3)
            payment_info = {
                "ref": rec.name,
                "pay_date": rec.date,
                "inv_paid": rec.ref,
                "amount": round(rec.amount, 3)
            }
            payments.append(payment_info)

        return {
            "status": 200,
            'response': payments,
            'items': len(payments),
            # 'percentage':paid/(not_paid+paid)*100,
            'paid': paid,
            "message": "Payments for the Provided Email"
        }
