
from odoo import http
from odoo.http import request, Response
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from ..validator import validator
from ..jwt_http import jwt_http 
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import math
import random
import smtplib
import xmlrpc.client

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
    @http.route('/api/password', type='json', auth='public', cors='*',  method=['POST'])
    def forgot_my_password(self,**kw):
        mail_user=request.env['ir.mail_server'].sudo().search([('smtp_port','=',465)])
        digits="0123456789"
        OTP=""
        data = json.loads(request.httprequest.data)
        email = data['email']
        if not email:
            response = {
                'code':400, 
                'message':'Email address cannot be empty'
            }
            return response
        partner =  request.env['res.partner'].sudo().search([('email', '=',email)])
        if not partner:
            response = {
                'code':400, 
                'message':'Email address does not exist'
            }
            return response
        if partner:
            for i in range(4):
                OTP+=digits[math.floor(random.random()*10)]
            otpMessage = OTP + " Is your reset Password  Code"
            subject='Password Reset Code'
            partner.sudo().write({'otp':OTP})
            s = smtplib.SMTP(mail_user.smtp_host, 587)
            s.starttls()
            s.login(mail_user.smtp_user, mail_user.smtp_pass)
            s.sendmail('&&&&&&&&&&&',email,otpMessage,subject)
        return {
                'code':200, 
                'status':'success',
                'message':'A code was Sent to your Email'
            }

    @http.route('/api/set/password', type='json', auth='public', cors='*',  method=['POST'])
    def set_new_password(self,**kw):
        mail_user=request.env['ir.mail_server'].sudo().search([('smtp_port','=',465)])
        digits="0123456789"
        OTP=""
        data = json.loads(request.httprequest.data)
        code = data['code']
        password = generate_password_hash(data['password'], method='sha256')
        data['password'] = password
        if not code:
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
        partner =  request.env['res.partner'].sudo().search([('otp', '=',code)])
        if not partner:
            response = {
                'code':400, 
                'message':'The Code is Invalid'
            }
            return response
        if partner:
            partner.sudo().write({'password':password})
            s = smtplib.SMTP(mail_user.smtp_host, 587)
            s.starttls()
            s.login(mail_user.smtp_user, mail_user.smtp_pass)
            s.sendmail('&&&&&&&&&&&',partner.email,'Your Password was successfully changed')
            partner.sudo().write({'otp':''})
        return {
                'code':400, 
                'status':'success',
                'message':'Password Successfully changed'
            }  
    
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