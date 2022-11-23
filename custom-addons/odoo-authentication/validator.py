import logging
import jwt
import re
import datetime
import traceback
import os
from odoo import http, service, registry, SUPERUSER_ID
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

regex = r"^[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"


class Validator:
    def is_valid_email(self, email):
        return re.search(regex, email)

    def key(self):
        return '8dxtZrbfRJQJd2NtPujww3OfwAUfKOXf'

    def create_token(self, user, password):
        try:
            exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            payload = {
                'exp': exp,
                'iat': datetime.datetime.utcnow(),
                'sub': user['id'],
                'lgn': user['email'],
                'name': user['name'],
                'vat': user['vat'],
                'phone': user['phone'],
            }

            token = jwt.encode(
                payload,
                self.key(),
                algorithm='HS256'
            )

            self.save_token(token, user['id'], exp)
            return token
        except Exception as ex:
            raise

    def save_token(self, token, uid, exp):
        request.env['jwt_provider.access_token'].sudo().create({
            'partner_id': uid,
            'expires': exp,
            'token': token,
        })

    def verify(self, token):
        record = request.env['jwt_provider.access_token'].sudo().search([
            ('token', '=', token),
        ],order='create_date desc', limit=1)

        if len(record) != 1:
            return False

        if record.is_expired:
            return False

        return True

    def verify_token(self, token):
    
        # try:
        result = {
            'status': False,
            'message': 'Token invalid or expired',
            'id': 0,
            'code': 400
        }
        payload = jwt.decode(token, self.key(), algorithms=["HS256"])
        if not self.verify(token):
            return self.errorToken()

        uid = payload['sub']
        if not uid:
            return self.errorToken()
        result['id'] = uid
        result['status'] = True
        result['code'] = 200
        result['message'] = 'Token valid'
        return result
    def errorToken(self):
        return {
            'message': 'Token invalid or expired',
            'code': 498,
            'status': False
        }

validator = Validator()