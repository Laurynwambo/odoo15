# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PosJsOrder(models.Model):
    _inherit = "pos.order"

    def _order_fields(self, ui_order):
        super(PosJsOrder, self)._order_fields(ui_order)
        print("Success ..........>")
