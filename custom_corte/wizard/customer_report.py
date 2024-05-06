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
from datetime import datetime, date
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from operator import itemgetter
from datetime import datetime, timedelta,date

class odoosv_customer_report(models.TransientModel):
    _name = 'odoosv.customer_report'
    partner_id=fields.Many2one(comodel_name='res.partner',string="Cliente")
    date_from=fields.Date("Desde")
    date_to=fields.Date("Hasta")

    def print_report(self):
        datas = {'ids': self._ids,
                 'date_from':self.date_from,
                 'date_to':self.date_to,
                 'partner_id':self.partner_id.id,
                 'partner_name':self.partner_id.name,
                 'form': self.read()[0],
                 'model': 'odoosv.customer_report'}
        customer=self.env['res.partner'].browse(self.partner_id.id)
        #raise ValidationError(str(self.partner_id.id))
        return self.env.ref('custom_corte.odoosv_customer_report').report_action(self.partner_id.id, data=datas)
    

class odoo_customer_report_partner(models.Model):
    _inherit='res.partner'

    def open_report(self):
        self.ensure_one()
        ctx = {'default_partner_id':self.id}
        action = {
            "name": _("Reporte de Cliente"),
            "type": "ir.actions.act_window",
            "res_model": "odoosv.customer_report",
            'target':'new',
            "view_type": "form",
            "view_mode": "form",
            'context':ctx,
        }
        return action
    

    def get_movimientos(self,partner_id,date_from,date_to):
        #self.ensure_one()
        #ordenes de venta
        #raise ValidationError('partner_id:'+str(partner_id)+' desde'+str(date_from)+' hasta:'+str(date_to))
        sale_orders=self.env['sale.order'].search([('date_order','>=',date_from),('date_order','<=',date_to),('partner_id','=',partner_id),('state','=','sale')],order='date_order asc')
        list=[]
        for l in sale_orders:
            dic={}
            dic['tipo']='Orden de venta'
            dic['fecha']=l.date_order.date()
            dic['numero']=l.name
            dic['descripcion']=l.paciente
            dic['monto']=l.amount_total
            dic['suma']=0
            list.append(dic)
        #Facturas
        facturas=self.env['account.move'].search([('invoice_date','>=',date_from),('invoice_date','<=',date_to),('partner_id','=',partner_id),('state','=','posted'),('move_type','=','out_invoice')],order='invoice_date asc')
        for l in facturas:
            dic={}
            dic['tipo']='Factura'
            dic['fecha']=l.invoice_date
            dic['numero']=l.tipo_documento_id.name+' '+l.doc_numero
            dic['descripcion']=l.x_paciente
            dic['monto']=l.amount_total
            dic['suma']=l.amount_total
            list.append(dic)
        #Notas
        notas=self.env['account.move'].search([('invoice_date','>=',date_from),('invoice_date','<=',date_to),('partner_id','=',partner_id),('state','=','posted'),('move_type','=','out_refund')],order='invoice_date asc')
        for l in notas:
            dic={}
            dic['tipo']='Nota de Credito'
            dic['fecha']=l.invoice_date
            dic['numero']=(l.tipo_documento_id.name if l.tipo_documento_id else '')+' '+(l.doc_numero if l.doc_numero else '')
            dic['descripcion']=l.x_paciente
            dic['monto']=l.amount_total
            dic['suma']=l.amount_total*-1
            list.append(dic)
        #pagos
        pagos=self.env['account.payment'].search([('date','>=',date_from),('date','<=',date_to),('partner_id','=',partner_id),('state','=','posted'),('payment_type','=','inbound')],order='date asc')
        for l in pagos:
            dic={}
            dic['tipo']='Pago'
            dic['fecha']=l.date
            dic['numero']=l.name
            dic['descripcion']=l.ref
            dic['monto']=l.amount
            dic['suma']=l.amount*-1
            list.append(dic)
        
        return sorted(list, key=itemgetter('fecha'))







    


