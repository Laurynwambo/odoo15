
from odoo import http
from odoo.http import request, Response
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
import json
from ..validator import validator
from ..jwt_http import jwt_http 
from werkzeug.security import generate_password_hash, check_password_hash

import logging
_logger = logging.getLogger(__name__)

SENSITIVE_FIELDS = ['password', 'password_crypt', 'new_password', 'create_uid', 'write_uid']

class JwtController(http.Controller):

    @http.route('/api/login', type='json', auth='public', cors='*',  method=['POST'])
    def login(self, **kw):
        data = json.loads(request.httprequest.data)
        email = data['email']
        password = data['password']
        if not email:
            response = {
                'code':400, 
                'message':'Email address cannot be empty'
            }
            return response
        if not password:
            response = {
                'code':400, 
                'message':'Password cannot be empty'
            }
            return response
        return jwt_http.do_login(email, password)
    
    @http.route('/api/forgot/password', type='json', auth='public', cors='*',  method=['POST'])
    def reset_password_link(self, **kw):
        data = json.loads(request.httprequest.data)
        email = data['email']
        if not email:
            response = {
                'code':400, 
                'message':'Email address cannot be empty'
            }
            _logger.error(response)
            return response
        partner =  request.env['res.partner'].sudo().search([('email', '=',email)])
        if not partner:
            response = {
                'code':400, 
                'message':'Email address does not exist'
            }
            _logger.error(response)
            return response
        password = ''
        token = validator.create_token(partner, password)
        reset_link = f'http://localhost:4200/auth/reset-password/{token}'
        reset_password = partner.send_partner_email_reset_email(reset_link, email)
        response = {
                'code':200, 
                'message':'Password Reset link has been sent to the email',
            }
        return response
        

    @http.route('/api/reset/password', type='json', auth='public', cors='*',  method=['POST'])
    def forgot_password(self, **kw):
        data = json.loads(request.httprequest.data)
        email = data['email']
        password = data['email']
        if not email:
            response = {
                'code':400, 
                'message':'Email address cannot be empty'
            }
            _logger.error(response)
            return response
        partner =  request.env['res.partner'].sudo().search([('email', '=',email)])
        if not partner:
            response = {
                'code':400, 
                'message':'Email address does not exist'
            }
            _logger.error(response)
            return response
        if not password:
            response = {
                'code':400, 
                'message':'Password cannot be empty'
            }
            _logger.error(response)
            return response
        password = generate_password_hash(data['password'], method='sha256')
        data = {
            "password": password
        }
        results = partner.write(data)
        response = {
            'code':200, 
            'message':'Password changed successfully',
            "results": results
        }
        return response

    @http.route('/api/me', type='json', auth='public', cors="*", method=['POST'])
    def me(self, **kw):
        http_method, body, headers, token = jwt_http.parse_request()
        _logger.error(token)
        result = validator.verify_token(token)
        _logger.error(result)
        if not result['status']:
            response = {
                'code':result['code'], 
                'message':result['message']
            }
            _logger.error(response)
            return response
        response = request.env["res.partner"].sudo().search([("id", "=", result['id'])])
        partner_details = {
            'email': response['email'],
            'name': response['name'],
            'phone': response['phone'],
            'country': response['country_id']['name'],
            'token': response['access_token_ids']['token']
        }
        resp = {
            'code':200, 
            'details':partner_details
        }
        return resp

    @http.route('/api/logout', type='json', auth='public', cors='*', method=['POST'])
    def logout(self, **kw):
        data = json.loads(request.httprequest.data)
        token = data['token']
        data.pop('token', None)
        result = validator.verify_token(token)
        if not result['status']:
            response = {
                'code':400, 
                'message':'Logout Failed'
            }
            _logger.error(response)
            return response

        jwt_http.do_logout(token)
        response = {
                'code':200, 
                'message':'Logout'
            }
        _logger.error(response)
        return response

    @http.route('/api/register', type='json', auth='public', cors='*',  method=['POST'])
    def register(self, **kw):
        data = json.loads(request.httprequest.data)
        email = data['email']
        password = generate_password_hash(data['password'], method='sha256')
        data['password'] = password
        name = data['name']
        vat = data['vat']
        phone = data['phone']
        if not email:
            response = {
                'code':422, 
                'message':'Email address cannot be empty'
            }
            return response
        if not vat:
            response = {
                'code':422, 
                'message':'Tax Id cannot be empty'
            }
            return response
        if not name:
            response = {
                'code':422, 
                'message':'Name cannot be empty'
            }
            _logger.error(response)
            return response
        if not password:
            response = {
                'code':422, 
                'message':'Password cannot be empty'
            }
            return response
        if not phone:
            response = {
                'code':422, 
                'message':'Phone cannot be empty'
            }
            return response
        if request.env["res.partner"].sudo().search([("email", "=", email)]):
            response = {
                'code':422, 
                'message':'Email address already existed'
            }
            return response
        if request.env["res.partner"].sudo().search([("phone", "=", phone)]):
            response = {
                'code':422, 
                'message':'Phone Number already existed'
            }
        if request.env["res.partner"].sudo().search([("vat", "=",vat)]):
            response = {
                'code':422, 
                'message':'Tax Id already existed'
            }
        register_response = {}
        try:           
            register_response = self._signup_with_values(data)
        except Exception as e:
            response = {
                'code':500, 
                'message':str(e)
            }
            _logger.error(response)
            return response
        return register_response

    def _signup_with_values(self, data):
        new_user = request.env['res.partner'].sudo().create(data)
        new_user.send_email()
        response = {
            'code': 200,
            'message': {
                'name': new_user.name,
                'number': new_user.vat,
                'email': new_user.email,
                'phone': new_user.phone
            }
        }
        return response

    def signup_email(self, data):
        user_sudo = request.env['res.partner'].sudo().search([('email', '=', data.get('email'))])