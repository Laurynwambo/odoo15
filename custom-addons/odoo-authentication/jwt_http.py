import simplejson as json
from odoo import http
from odoo.http import request, Response
from .validator import validator
from odoo.exceptions import AccessError, AccessDenied
from werkzeug.security import generate_password_hash, check_password_hash

return_fields = ['id', 'login', 'name', 'company_id']
import logging
_logger = logging.getLogger(__name__)
class JwtHttp:

    def get_state(self):
        return {
            'd': request.session.db
        }

    def parse_request(self):
        http_method = request.httprequest.method
        try:
            body = http.request.params
        except Exception:
            body = {}

        headers = dict(list(request.httprequest.headers.items()))
        if 'wsgi.input' in headers:
            del headers['wsgi.input']
        if 'wsgi.errors' in headers:
            del headers['wsgi.errors']
        if 'HTTP_AUTHORIZATION' in headers:
            headers['Authorization'] = headers['HTTP_AUTHORIZATION']

        # extract token
        token = ''
        if 'Authorization' in headers:
            try:
                # Bearer token_string
                token = headers['Authorization'].split(' ')[1]
            except Exception:
                pass

        return http_method, body, headers, token

    def date2str(self, d, f='%Y-%m-%d %H:%M:%S'):
        """
        Convert datetime to string
            :param self: 
            :param d: datetime object
            :param f='%Y-%m-%d%H:%M:%S': string format
        """
        try:
            s = d.strftime(f)
        except:
            s = None
        finally:
            return s

    def response(self, success=True, message=None, data=None, code=200):
        """
        Create a HTTP Response for controller 
            :param success=True indicate this response is successful or not
            :param message=None message string
            :param data=None data to return
            :param code=200 http status code
        """
        payload = json.dumps({
            'success': success,
            'message': message,
            'data': data,
        }, encoding='utf-8')

        return Response(payload, status=code, headers=[
            ('Content-Type', 'application/json'),
        ])
    
    def success(self, success = True, message = None, data = None, code=200):
        return {
            'code': code,
            'success': success,
            'data': data
        }

    def response_500(self, message='Internal Server Error', data=None):
        return self.response(success=False, message=message, data=data, code=500)

    def response_404(self, message='404 Not Found', data=None):
        return self.response(success=False, message=message, data=data, code=404)

    def response_403(self, message='403 Forbidden', data=None):
        return self.response(success=False, message=message, data=data, code=403)

    def errcode(self, code, message=None):
        return self.response(success=False, code=code, message=message)

    def do_login(self, email, password):
        # get current db
        state = self.get_state()
        try:
            # uid = request.session.authenticate(state['d'], login, password)
            partner = request.env["res.partner"].sudo().search([("email", "=", email)])
            if (check_password_hash(partner['password'], password)):
                # login success, generate token
                # user = request.env["res.partner"].sudo().search([("email", "=", email)])
                token = validator.create_token(partner, password)
                data={ 'user_name': partner.name, 'email': partner.email,'user_id': partner.id, 'token_type': 'Bearer', 'access_token': token, 'code':200 }
                return data
            else:
                response = {
                'code':401, 
                'message':'Incorrect Login'
                }
                return response
#                 return self.errcode(code=422, message='Incorrect Login')
        except AccessError as aee:
            response = {
                'code':401, 
                'message': "Access error" % aee.name
                }
            return response
#             return self.errcode(code=422, message= "Access error" % aee.name)
        except AccessDenied as ade:
            response = {
                'code':401, 
                'message': "Email, password or db invalid"
                }
            return response
#             return self.errcode(code=422, message= "Email, password or db invalid")
        except Exception as e:
            _logger.error(e)
            _logger.error('ODOOOO DATABASE')
            response = {
                'code':401, 
                'message': "Wrong database name ,Check again {}".format((e))
                }
            return response
        

    def do_logout(self, token):
        self.cleanup()
        request.env['jwt_provider.access_token'].sudo().search([
            ('token', '=', token)
        ]).unlink()

    def cleanup(self):
        request.session.logout()


jwt_http = JwtHttp()