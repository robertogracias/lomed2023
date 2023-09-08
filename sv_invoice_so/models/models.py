# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#
##############################################################################
import base64
import json
import requests
import logging
import time
from datetime import datetime
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)


class odoosv_caja(models.Model):
    _inherit='odoosv.caja'
    entregar_producto=fields.Boolean("Crear SO y Entregar Producto")

class odoosv_move(models.Model):
    _inherit='account.move'
    sale_order_id=fields.Many2one(comodel_name='sale.order',string='Orden de venta',copy=False)
    #pricelist_id = fields.Many2one(comodel_name="product.pricelist", string="Pricelist", readonly=True, states={"draft": [("readonly", False)]},)


    def action_post(self):
        #inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(odoosv_move, self).action_post()
        self.sudo().create_saleorder()
        return res

    def create_saleorder(self):
        for r in self:
            if (r.move_type=='out_invoice') and r.invoice_origin==False:
                if r.caja_id.entregar_producto:
                    dic={}
                    dic['partner_id']=r.partner_id.id
                    if r.invoice_payment_term_id:
                        dic['payment_term_id']=r.invoice_payment_term_id.id
                    if r.partner_shipping_id:
                        dic['partner_shipping_id']=r.partner_shipping_id.id                    
                    if r.caja_id:
                        dic['caja_id']=r.caja_id.id
                        if r.caja_id.warehouse_id:
                            dic['warehouse_id']=r.caja_id.warehouse_id.id
                    order=self.env['sale.order'].create(dic)
                    r.write({'sale_order_id':order.id,'invoice_origin':order.name})
                    for l in r.invoice_line_ids:
                        dicl={}
                        dicl['product_id']=l.product_id.id
                        dicl['name']=l.name
                        dicl['currency_id']=l.currency_id.id
                        dicl['price_unit']=l.price_unit
                        dicl['product_uom_qty']=l.quantity
                        dicl['product_uom']=l.product_uom_id.id
                        tax=[]
                        for t in l.tax_ids:
                            tax.append(t.id)
                            dicl['tax_id']=[(6,0,tax)]
                        dicl['order_id']=order.id
                        dicl['invoice_lines']=[(6,0,[l.id])]
                        linea=self.env['sale.order.line'].create(dicl)
                    order.action_confirm()
                    for p in order.picking_ids:
                        if p.state=='assigned':
                            for l in p.move_line_ids_without_package:
                                l.write({'qty_done':l.reserved_qty})
                            p.button_validate()




