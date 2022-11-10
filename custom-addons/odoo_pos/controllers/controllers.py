# -*- coding: utf-8 -*-
# from odoo import http


# class OdooPos(http.Controller):
#     @http.route('/odoo_pos/odoo_pos', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_pos/odoo_pos/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_pos.listing', {
#             'root': '/odoo_pos/odoo_pos',
#             'objects': http.request.env['odoo_pos.odoo_pos'].search([]),
#         })

#     @http.route('/odoo_pos/odoo_pos/objects/<model("odoo_pos.odoo_pos"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_pos.object', {
#             'object': obj
#         })
