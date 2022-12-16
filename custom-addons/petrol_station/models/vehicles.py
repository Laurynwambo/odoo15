# -*- coding: utf-8 -*-

from email import message
from email.policy import default
from odoo import models, fields, api
from datetime import date

import logging

_logger = logging.getLogger(__name__)


class VehicleDetails(models.Model):
    _name = 'vehicle.details'
    _inherit= ['mail.thread', 'mail.activity.mixin']
    _description = 'Vehicle Details'
   
    image=fields.Image(string="Vehicle")
    v_number=fields.Char(string="Vehicle Number")
    owner=fields.Many2one('res.partner',string="Owner's Name")
    mobile=fields.Char(string="Phone Number")
    o_address=fields.Char(string="Current Address")
    vat_no=fields.Char(string="PAN/VAT No:")
    make=fields.Char(string="Vehicle Make")
    model=fields.Char(string="Vehicle's Model") 
    year=fields.Integer(string="Year of Manufucture") 
    active= fields.Boolean(string="active", default=True, tracking=True) 
    ref=fields.Char(string="Reference Number") 
    services=fields.Many2many('service.available', string="Services")

    @api.model
    def create(self, vals):
        _logger.info("create method overwrite with vals: %s" % vals)
        return super(VehicleDetails, self).create(vals)

    # @api.depends('value')
    # def _value_pc(self):
    #     for record in self:
    #         record.value2 = float(record.value) / 100



class ServicesAvailable(models.Model):
    _name = 'service.available'
    _description = 'Services'

    name=fields.Char(string="Name", required=True)
    active=fields.Boolean(string="active", default=True)
    color=fields.Integer(string="Color")
    # color_2=fields.Char(string="Color 2")
    
@api.model
def create(self, vals):
        _logger.info("create method overwrite with vals: %s" % vals)
        return super(ServicesAvailable, self).create(vals)
    


    