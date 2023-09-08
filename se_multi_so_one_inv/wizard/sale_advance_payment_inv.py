# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class sale_advance_payment_inv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    def _create_invoice(self, order, so_line, amount):
        res = super(sale_advance_payment_inv, self)._create_invoice(order, so_line, amount)
        for one_inv_line in res.invoice_line_ids:
            one_inv_line.write({'sale_order_line_id': so_line.id})
        return res
