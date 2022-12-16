# -*- coding: utf-8 -*-


from odoo import models,_, fields, api
from datetime import date

import logging

_logger = logging.getLogger(__name__)
class ProductProduct(models.Model):
    _inherit = 'product.product'

    on_app=fields.Boolean('On App',default=False)
class FuelsStock(models.Model):
    _name = 'fuels.stock'
    _inherit= ['mail.thread', 'mail.activity.mixin']
    _description = 'Fuel Stock'
    _rec_name=('product_name')

    product_name=fields.Many2one(comodel_name='product.product', string="Product")
    start=fields.Float(string="Start Readings",store=True)
    name_seq = fields.Char(string='Name', required=True,readonly=True, default=lambda self: _('New'))
    salesperson=fields.Many2one('res.users', string="Sales Person")
    price = fields.Float(related="product_name.list_price")
    date=fields.Date(string="Today's Date")
    sold=fields.Float(compute="_compute_units_sold",string="Units Sold")
    stop=fields.Float(string="Stop Readings")
    sales=fields.Float(compute="_compute_total_sales",string="Total Sales")
    active= fields.Boolean(string="active", default=True, tracking=True) 
   
    
    
    
    
   
    priority=fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2','High'),
        ('3','Very High')

    ], string="Priority")

    state=fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved','Approved'),
        ('cancel','Cancel'),
       
        

    ], default="draft",string="Status", required=True)

    def action_approved(self):
        for rec in self:
            rec.state='approved'
    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code(
                'fuels.stock.sequence') or _('New')
            res = super(FuelsStock, self).create(vals)
            return res
    def action_confirmed(self):
        self.ensure_one()
        rec = self
        rec.state='confirmed' 
        tmpl = rec.env["product.template"].search([("id", "=", rec.product_name.product_tmpl_id.id)], limit=1)
        return tmpl.with_context({"default_product_id":rec.product_name.id,\
            "default_new_quantity":rec.stop}).action_update_quantity_on_hand()
        
                    
            
        
    def action_draft(self):
        for rec in self:
            rec.state='draft'
            
    def action_cancel(self):
        for rec in self:
            rec.state='cancel'
                      
            
            
            
    @api.depends('sales')
    def _compute_total_sales(self):
        for rec in self:
           
              rec.sales = ((rec.start-rec.stop)*rec.price)
              
    @api.depends('sold')
    def _compute_units_sold(self):
        for rec in self:
           
              rec.sold = (rec.start-rec.stop)      

    @api.model
    def create(self, vals):
        _logger.info("create method overwrite with vals: %s" % vals)
        # move_lines = []
        # for rec in self:
        #   move_lines.append() "invoice_line_ids": move_lines
        # moves = self.env["account.move"].create({'partner_id': vals["n_owner"], 'move_type': 'out_invoice', 
        # 'invoice_date': date.today(), })
        # moves.action_post()
        return super(FuelsStock, self).create(vals)

    # @api.depends('value')
    # def _value_pc(self):
    #     for record in self:
    #         record.value2 = float(record.value) / 100
    
    

    

    