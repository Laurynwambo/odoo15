# -*- coding: utf-8 -*-
# from odoo import http


# class MultiView(http.Controller):
#     @http.route('/multi_view/multi_view', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/multi_view/multi_view/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('multi_view.listing', {
#             'root': '/multi_view/multi_view',
#             'objects': http.request.env['multi_view.multi_view'].search([]),
#         })

#     @http.route('/multi_view/multi_view/objects/<model("multi_view.multi_view"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('multi_view.object', {
#             'object': obj
#         })
