from werkzeug.security import generate_password_hash, check_password_hash
from ..validator import validator
from odoo.http import request
from odoo import http
import datetime
import random
import json
import math
import jwt

import logging

_logger = logging.getLogger(__name__)
today = datetime.date.today()

SENSITIVE_FIELDS = ['password', 'password_crypt', 'new_password', 'create_uid', 'write_uid']


class JwtController(http.Controller):
    def key(self):
        return '8dxtZrbfRJQJd2NtPujww3OfwAUfKOXf'

    def _prepare_final_email_values(self, employee):
        mail_user = request.env['ir.mail_server'].sudo().search([('smtp_port', '=', 465)])
        subject = f"Password Changed Successfully"
        mail_obj = request.env['mail.mail']
        email_from = mail_user.smtp_user
        email_to = employee.work_email
        body_html = f"""
            <html>
            <body>
            <div style="margin:0px;padding: 0px;">
                <p style="padding: 0px; font-size: 13px;">
                    Hello {employee.name} !!,
                    <br/>
                    Your password was successfuly changed.
                    <br/> 
                    We are happy to serve you the best.
                    <br/>
                    .
                <br/>
                </p>

                <p>
                Best Regards
                    <br/>
                The Team</p>
            <br/>
            </div>
            </body>
            </html>
        """
        mail = mail_obj.sudo().create({
            'body_html': body_html,
            'subject': subject,
            'email_from': email_from,
            'email_to': email_to
        })
        mail.send()
        return mail

    def _prepare_otp_email_values(self, employee):
        mail_user = request.env['ir.mail_server'].sudo().search([('smtp_port', '=', 465)])
        mail_obj = request.env['mail.mail']
        email_from = mail_user.smtp_user
        subject = f"Forgot My Password"
        email_to = employee.work_email
        body_html = f"""
            <html>
            <body>
            <div style="margin:0px;padding: 0px;">
                <p style="padding: 0px; font-size: 13px;">
                    Hello {employee.name} !!,
                    <br/>
                    Your request to reset password was successfuly.
                    <br/>
                    use {employee.otp} to reset your Password.
                    <br/>
                    Otp is Valid for <strong>1 minute</strong>
                    <br/> 
                    if you did not request for this ignore this message.
                    <br/>
                    .
                <br/>
                </p>

                <p>Best Regards
                    <br/>
                The Team</p>
            <br/>
            </div>
            </body>
            </html>
        """
        mail = mail_obj.sudo().create({
            'body_html': body_html,
            'subject': subject,
            'email_from': email_from,
            'email_to': email_to
        })
        mail.send()
        return mail

    def _prepare_registration_email_values(self, new_employee):
        mail_user = request.env['ir.mail_server'].sudo().search([('smtp_port', '=', 465)])
        mail_obj = request.env['mail.mail']
        email_from = mail_user.smtp_user
        subject = f"SuccessFully Registration"
        email_to = new_employee.work_email
        body_html = f"""
            <html>
            <body>
            <div style="margin:0px;padding: 0px;">
                <p style="padding: 0px; font-size: 13px;">
                    Hello {new_employee.name} !!,
                    <br/>
                    Your Account was successfuly Registered with us.
                    <br/>
                    We hope you will enjoy the best experience as
                    <br/> 
                    you track all your invoices and payments.
                    <br/>
                    .
                <br/>
                </p>

                <p>Best Regards
                    <br/>
                The Team</p>
            <br/>
            </div>
            </body>
            </html>
        """
        mail = mail_obj.sudo().create({
            'body_html': body_html,
            'subject': subject,
            'email_from': email_from,
            'email_to': email_to
        })
        mail.send()
        return mail

    @http.route('/v1/employee/login', type='json', auth='public', cors='*', method=['POST'])
    def login(self, **kw):
        exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        data = json.loads(request.httprequest.data)
        email = data['email']
        password = data['password']
        if not email:
            response = {
                'code': 400,
                'message': 'Email address cannot be empty'
            }
            return response
        if not password:
            response = {
                'code': 400,
                'message': 'Password cannot be empty'
            }
            return response
        employee = request.env['hr.employee'].sudo().search([('work_email', '=', email)])
        user = request.env['res.users'].sudo().search([('login','=',data['email'])]).has_group('sales_team.group_sale_manager')
        if employee:
            user = check_password_hash(employee['password'], password)
            if user:
                payload = {
                    'exp': exp,
                    'iat': datetime.datetime.utcnow(),
                    'sub': employee['id'],
                    'lgn': employee['work_email'],
                    'name': employee['name'],
                    'phone': employee['work_phone']
                }
                token = jwt.encode(payload, self.key(), algorithm='HS256')
                request.env['jwt_provider.access_token'].sudo().create({'employee_id': employee.id, 'expires': exp, 'token': token})
                age=today.year-employee.birthday.year
                return {
                    'phone': employee.work_phone,
                    'user_name': employee.name,
                    'email': employee.work_email,
                    'age': age,
                    'is_manager':user,
                    'gender': employee['gender'],
                    'user_id': employee.id,
                    'token_type': 'Bearer',
                    'access_token': token,
                    'code': 200
                }

            else:
                return {
                    'code': 401,
                    'status': 'failed',
                    'message': 'Your Password is Incorrect'
                }
        else:
            return {
                'code': 401,
                'status': 'failed',
                'message': 'Email address does not Exist'
            }

    @http.route('/v1/employee/password', type='json', auth='public', cors='*', method=['POST'])
    def forgot_my_password(self, **kw):
        digits = "0123456789"
        OTP = ""
        data = json.loads(request.httprequest.data)
        _logger.error(data)
        _logger.error('THE FORGOT PAYLOAD')
        email = data['email']
        if not email:
            response = {
                'code': 400,
                'message': 'Email address cannot be empty'
            }
            return response
        employee = request.env['hr.employee'].sudo().search([('work_email', '=', email)])
        if not employee:
            response = {
                'code': 400,
                'message': 'Email address does not exist'
            }
            return response
        if employee:
            for i in range(4):
                OTP += digits[math.floor(random.random() * 10)]
            employee.sudo().write({'otp': OTP,'when_sent':today})
            self._prepare_otp_email_values(employee)
        return {
            'code': 200,
            'status': 'success',
            "email":employee.work_email,
            'message': 'A code was Sent to your Email'
        }

    @http.route('/v1/employee/set/password', type='json', auth='public', cors='*', method=['POST'])
    def set_new_password(self, **kw):
        data = json.loads(request.httprequest.data)
        code = data['code']
        password = generate_password_hash(data['password'], method='sha256')
        data['password'] = password
        if not code:
            response = {
                'code': 400,
                'message': 'Verrification Code cannot be empty'
            }
            return response
        if not password:
            response = {
                'code': 400,
                'message': 'Password cannot be empty'
            }
            return response
        employee = request.env['hr.employee'].sudo().search([('otp', '=', code)])
        if not employee:
            response = {
                'code': 400,
                'message': 'The Code is Invalid'
            }
            return response
        if employee:
            diff=((today-employee.when_sent).total_seconds())/60
            if diff <1:
                employee.sudo().write({'password': password})
                employee.sudo().write({'otp': ''})
                self._prepare_final_email_values(employee)
                return {
                    'code': 200,
                    'status': 'success',
                    'message': 'Password Successfully changed'
                }
            else:
                return {
                    'code':402,
                    'status': 'success',
                    'message': 'The Code has expired'
                }


    @http.route('/v1/employee/logout', type='json', auth='public', cors='*', method=['POST'])
    def logout(self, **kw):
        data = json.loads(request.httprequest.data)
        token = data['token']
        data.pop('token', None)
        result = validator.verify_token(token)
        if not result['status']:
            response = {
                'code': 400,
                'message': 'Logout Failed'
            }
            return response
        logout = request.env['jwt_provider.access_token'].sudo().search([('token', '=', token)])
        logout.sudo().unlink()
        response = {
            'code': 200,
            'message': 'Logout'
        }
        return response

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
    @http.route('/v1/employee/register', type='json', auth='public', cors='*', method=['POST'])
    def register(self, **kw):
        data = json.loads(request.httprequest.data)
        email = data['email']
        password = generate_password_hash(data['password'], method='sha256')
        data['password'] = password
        name = data['name']
        phone = data['phone']
        if not email:
            response = {
                'code': 422,
                'message': 'Email address cannot be empty'
            }
            return response
        if not name:
            response = {
                'code': 422,
                'message': 'Name cannot be empty'
            }
            _logger.error(response)
            return response
        if not password:
            response = {
                'code': 422,
                'message': 'Password cannot be empty'
            }
            return response
        if not phone:
            response = {
                'code': 422,
                'message': 'Phone cannot be empty'
            }
            return response
        if request.env["hr.employee"].sudo().search([("work_email", "=", email)]):
            response = {
                'code': 422,
                'message': 'Email address already existed'
            }
            return response
        if request.env["hr.employee"].sudo().search([("work_phone", "=", phone)]):
            response = {
                'code': 422,
                'message': 'Phone Number already existed'
            }
        employee = request.env['hr.employee'].sudo().create({
            'work_email':email,
            'work_phone':phone,
            'name':name,
            'password':password
        })
        if employee:
            self._prepare_registration_email_values(employee)
            response = {
                'code': 200,
                'message': {
                    'name': employee.name,
                    'email': employee.work_email,
                    'phone': employee.work_phone
                }
            }
        return response
