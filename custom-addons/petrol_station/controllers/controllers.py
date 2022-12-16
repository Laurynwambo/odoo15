# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class PetrolStation(http.Controller):
    @http.route('/petrolstation', auth='public', website=True)
    def index(self, **kw):
        # return "Hello, world"
        test = request.env['stock.fuel'].sudo().search([])
        print("Stock.... ", test)
        return request.render('petrol_station.tmp_sales_data', {
            'test': test
        })
       
       
   
    @http.route('/create_vendor',type='http',auth='user')
    def create_user(self, rec):
        if request.jsonrequest:
            print('rec', rec)
            if rec['vendor']:
               vals= {
                    'vendor': rec['vendor']
                }
               new_vendor = request.env['stock.fuel'].sudo().create(vals)
               args = {
                   'success': True,
                   'message': 'Success',
                   'ID': new_vendor.id
               }
        return new_vendor
    
    @http.route('/get_vendors', type='http', auth='public')
    def get_vendors(self):
        vendors_rec = request.env['stock.fuel'].search([])
        vendors = []
        for rec in vendors_rec:
            vals = {
                'id': rec.id,
                'vendor': rec.vendor,
            }
            vendors.append(vals)
        print('vendors', vendors)
        data= {
            'success': True,
            'message': 'Success',
        }
        return data
    
    
            
        
        
        

    # @http.route('/petrol_station/petrol_station/objects', auth='public')
    # def list(self, **kw):
    #     return http.request.render('petrol_station.listing', {
    #         'root': '/petrol_station/petrol_station',
    #         'objects': http.request.env['petrol_station.petrol_station'].search([]),
    #     })

    # @http.route('/petrol_station/petrol_station/objects/<model("petrol_station.petrol_station"):obj>', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('petrol_station.object', {
    #         'object': obj
    #     })
