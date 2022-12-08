from odoo import http
from odoo.http import request, Response
import logging
import jwt
import json

_logger = logging.getLogger(__name__)
secret = "8dxtZrbfRJQJd2NtPujww3OfwAUfKOXf"

class MobileConnect(http.Controller):
    def _prepare_validation_key(self, token):
        verify=jwt.decode(token,secret,algorithms=["HS256"])
        if verify['sub']:
            return True

        else:
            return {
                'code':403,
                'status':'failed',
                'message': "Your Not Authorized"
            }
    @http.route('/v1/customer/invoices', type='json', auth='public', cors='*', method=['POST'])
    def get_invoices(self, email=None):
        data = json.loads(request.httprequest.data)
        verify=self._prepare_validation_key(data["token"])
        if verify:
            invoices = []
            paid = 0.00
            not_paid = 0.00
            if not data['email']:
                response = {
                    'code': 400,
                    'message': 'Email address not provided'
                }
                return response
            invoice = request.env['account.move'].sudo().search([
                ("payment_state", "in", ["not_paid", "partial"]),
                ('state', '=', 'posted'),
                ('partner_id.email', '=', data['email'])
            ])
            for rec in invoice:
                not_paid += rec.amount_residual
                inv_info = {
                    "ref": rec.name,
                    "inv_date": rec.invoice_date,
                    "due_date": rec.invoice_date_due,
                    "due_amount": round(rec.amount_residual, 2),
                    "inv_status": rec.payment_state,
                    "paid_amount": round(rec.amount_total-rec.amount_residual, 2)
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
        else:
            return {
                'code':403,
                'status':'failed',
                'message': "Your Not Authorized"
            }
    @http.route('/v1/customer/payments', type='json', auth='public', cors='*', method=['POST'])
    def get_payments(self, email=None):
        data = json.loads(request.httprequest.data)
        verify=self._prepare_validation_key(data['token'])
        if verify:
            payments = []
            paid = 0.00
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
        return {
                'code':403,
                'status':'failed',
                'message': "Your Not Authorized"
            }
