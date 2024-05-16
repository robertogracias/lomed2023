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
from datetime import datetime, timedelta,date

class odoosv_lomedcorte(models.Model):
    _inherit = 'odoosv.cierre'
    def gettotalpagos(self):
        total= 0.00
        for item in self.cierrepago_ids:
            total += item.monto
        return total
    def gettotalperpago(self,pago):
        totalpago = 0.00
        for item in self.cierrepago_ids:
            if item.journal_id.code == pago:
                totalpago = item.monto
        return totalpago
    def get_totalventa(self):
        totalventa = 0.00
        facturas=self.env['account.move'].search([('cierre_id','=',self.id)])
        for factura in facturas:
            totalventa += factura.amount_total
        return totalventa
    def get_ventastotal(self, contado = 1):
        totalcontado = 0.00
        if contado:
            facturas=self.env['account.move'].search([('cierre_id','=',self.id),('invoice_payment_term_id','=', 1)])
        else:
            facturas=self.env['account.move'].search([('cierre_id','=',self.id),('invoice_payment_term_id','!=', 1)])
        for factura in facturas:
            totalcontado += factura.amount_total
        return totalcontado
    def get_pago_diarios(self, diarios):
        totalpago = 0.00
        for item in self.cierrepago_ids:
            for codigo in diarios:
                if item.journal_id.code == codigo:
                    totalpago = item.monto
        return totalpago
    def get_total_facrectificativa_c_e(self,credito = 1):
        totalcredito =0.00
        
        if credito:
            id = self.env['odoosv.fiscal.document'].search([('formato','=', 'NCREDITO'),('caja_id','=',self.caja_id.id)])
        else:
            id = self.env['odoosv.fiscal.document'].search([('formato','=', 'NotaDebito'),('caja_id','=',self.caja_id.id)])
        facturas=self.env['account.move'].search([('cierre_id','=',self.id),('tipo_documento_id','=', id.id),('move_type', '=', 'in_refund')])
        for factura in facturas:
            totalcredito += factura.amount_total
        return totalcredito
    def get_total_rectificativa(self):
        total = 0.00
        facturas=self.env['account.move'].search([('cierre_id','=',self.id),('move_type', '=', 'in_refund'),('state', '=', 'paid')])
        for factura in facturas:
            total += factura.amount_total
        return total
    def get_total_pago_rectifi(self):
        total = 0.00
        facturas=self.env['account.move'].search([('cierre_id','=',self.id),('move_type', '=', 'in_refund')])
        for factura in facturas:
            total += factura.amount_total
        return total
    def get_total_comprovante_retencion(self):
        tipodocumento = self.env['odoosv.fiscal.document'].search([('name','like', 'Comprobante de Retención'),('caja_id','=',self.caja_id.id)])
        totales = {}
        totales['ivatotal'] =0.00
        totales['retenidototal']=0.00
        totales['total']=0.00
        total = 0.00
        facturas=self.env['account.move'].search([('cierre_id','=',self.id),('tipo_documento_id', '=', tipodocumento.id)])
        for factura in facturas:
            totales['total']+= factura.amount_total
            lineas = self.env['account.move.line'].search([('move_id','=',factura.id),('tax_group_id.code','=','iva')]) 
            for line in lineas:
                totales['ivatotal'] = line.credit
            lineas1 = self.env['account.move.line'].search([('move_id','=',factura.id),('tax_group_id.code','=','retenido')])
            for line1 in lineas1:
                totales['retenidototal'] = line1.credit
        return totales
    def get_total_comprovante_retencion_iva(self):
        tipodocumento = self.env['odoosv.fiscal.document'].search([('name','like', 'Comprobante de Retención'),('caja_id','=',self.caja_id.id)])
        
        total = 0.00
        facturas=self.env['account.move'].search([('cierre_id','=',self.id),('tipo_documento_id', '=', tipodocumento.id)])
        for factura in facturas:
            total+= factura.amount_total
        return total
    def get_total_comprovante_retencion_retenido(self):
        tipodocumento = self.env['odoosv.fiscal.document'].search([('name','like', 'Comprobante de Retención'),('caja_id','=',self.caja_id.id)])
        
        total = 0.00
        facturas=self.env['account.move'].search([('cierre_id','=',self.id),('tipo_documento_id', '=', tipodocumento.id)])
        for factura in facturas:
            total+= factura.amount_total
        return total
    def get_documentos(self, name):
        #documentos = self.env['odoosv.fiscal.document'].search([('caja_id','=',self.caja_id.id)])
        facturas = []
        """for documento in documentos:
            facturas=self.env['account.move'].search([('cierre_id','=',self.id),('tipo_documento', '=', documento.id),('state','!=','draft'),('state','!=','cancel')])
            dic = {}
            dic['name'] = documento.name
            dic['cantidad'] = len(facturas)
            #anulados
            anulados=self.env['account.move'].search([('cierre_id','=',self.id),('tipo_documento', '=', documento.id),('state','=','cancel')])
            dic['anulados'] = len(anulados)"""
        #agrupando
        groups=self.env['account.move'].read_group([('invoice_date','=',self.fecha_cierre),('move_type','in',['out_invoice','out_refund']),('state','!=','draft'),('state','!=','cancel'),('caja_id','=',self.caja_id.id),('tipo_documento_id.name','=', name)],['tipo_documento_id.name','min_doc:min(doc_numero)','max_doc:max(doc_numero)','count_doc:count(doc_numero)'],['tipo_documento_id'],limit=1)            
        
        for r in groups:                
            doc={}
            tipo=self.env['odoosv.fiscal.document'].browse(r['tipo_documento_id'][0])    
            doc['name']=tipo.name
            doc['min_doc']=r['min_doc']
            doc['max_doc']=r['max_doc']
            doc['cantidad']=r['count_doc']
            anulados=self.env['account.move'].search([('invoice_date','=',self.fecha_cierre),('move_type','in',['out_invoice','out_refund']),('tipo_documento_id', '=', tipo.id),('state','=','cancel')])
            doc['anulados'] = len(anulados)
            facturas.append(doc)
        return facturas
    def get_today_invoices(self, journal_id):
        current=self.fecha_cierre
        dia=int(datetime.strftime(current, '%d'))
        mes=int(datetime.strftime(current, '%m'))
        anio=int(datetime.strftime(current, '%Y'))
        hoy_1=datetime(anio,mes,dia,0,0,1)
        hoy_2=datetime(anio,mes,dia,23,59,59)
        hoy_1=hoy_1+timedelta(hours=6)
        hoy_2=hoy_2+timedelta(hours=6)
        #invoices = []
        #facturas = self.env['account.move'].search([('invoice_date','=',self.fecha_cierre),('move_type','in',['out_invoice','out_refund']),('state','=','cancel'),('payment_state', '=','paid')], order='tipo_documento_id')
        #pagos=self.env['account.payment'].search([('date','>=',hoy_1),('date','<=',hoy_2),('journal_id', '=', journal_id),('state','!=','cancel'),('state','!=','draft'),('payment_type', '=', 'inbound'),('caja_id','=',self.caja_id.id)])
        pagos=self.env['account.payment'].search([('date','>=',hoy_1),('date','<=',hoy_2),('journal_id', '=', journal_id),('state','!=','cancel'),('state','!=','draft'),('payment_type', '=', 'inbound'),('caja_id','=',self.caja_id.id)])
        
        return pagos
    def get_account_move(self, ref):
        current=self.fecha_cierre
        dia=int(datetime.strftime(current, '%d'))
        mes=int(datetime.strftime(current, '%m'))
        anio=int(datetime.strftime(current, '%Y'))
        hoy_1=datetime(anio,mes,dia,0,0,1)
        hoy_2=datetime(anio,mes,dia,23,59,59)
        hoy_1=hoy_1+timedelta(hours=6)
        hoy_2=hoy_2+timedelta(hours=6)
        #move = payment._get_reconciled_invoices()
        current=self.fecha_cierre
        array = ref.split(':')
        pago = self.env['account.move'].search([('doc_numero','=',array[1]), ('tipo_documento_id.name', '=',array[0])])
        return pago
    def pagos(self,id):
        pagos3=self.env['account.payment'].search(['&',('cierre_id','=',self.id),('payment_type','=','inbound'),('journal_id','=',id)])
        return pagos3   
    def obtenerinvoices(self,paymend_id):
        invoices = []
        if paymend_id:
            movelinereconcilied =self.env['account.move.line'].search([('payment_id','=', paymend_id),('full_reconcile_id', '!=', False)])
            invoices =self.env['account.move.line'].search([('full_reconcile_id', '=', movelinereconcilied.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.tipo_documento_id.name','!=','Comprobante de Retencón')])
        return invoices
    #move_tyep in_refund

    def gettax(self,code,moveid):
        valor = 0.00
        move_line = self.env['account.move.line'].search([('move_id','=',moveid),('tax_group_id.code','=',code)])
        for item in move_line:
            valor += item.credit
        return valor
    def get_compro_retencion(self, diario_id):
        invoices = []
        if diario_id:
            movelinereconcilied =self.env['account.move.line'].search([('journal_id','=', diario_id),('full_reconcile_id', '!=', False)])
            for line in movelinereconcilied:
                invoices.append(self.env['account.move.line'].search([('full_reconcile_id', '=', line.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.tipo_documento_id.name','=','Comprobante de Retencón')]))
        return invoices
    def total_notas_credito(self):
        invoices =self.env['account.move.line'].search([('full_reconcile_id', '=', movelinereconcilied.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.tipo_documento_id.name','=','Comprobante de Retencón')])
    
    def get_pago_diarios_recupe(self, diarios):
        totalpago = 0.00
        current=self.fecha_cierre
        dia=int(datetime.strftime(current, '%d'))
        mes=int(datetime.strftime(current, '%m'))
        anio=int(datetime.strftime(current, '%Y'))
        hoy_1=datetime(anio,mes,dia,0,0,1)
        hoy_1=hoy_1+timedelta(hours=6)
        for item in self.pago_ids:
            for codigo in diarios:
                if item.journal_id.code == codigo:
                    movelinereconcilied =self.env['account.move.line'].search([('payment_id','=', item.id),('full_reconcile_id', '!=', False)])
                    invoices =self.env['account.move.line'].search([('full_reconcile_id', '=', movelinereconcilied.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.invoice_date','<',hoy_1)])
                    if len(invoices) > 0:
                        totalpago = item.monto
        return totalpago
    
    def get_devolucione_invoice(self):
        invoices = []
        if paymend_id:
            movelinereconcilied =self.env['account.move.line'].search([('payment_id','=', paymend_id),('full_reconcile_id', '!=', False)])
            invoices =self.env['account.move.line'].search([('full_reconcile_id', '=', movelinereconcilied.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.tipo_documento_id.name','!=','Comprobante de Retencón')])
        return invoices
    def get_abonos(self):
        total = 0.00
        current=self.fecha_cierre
        dia=int(datetime.strftime(current, '%d'))
        mes=int(datetime.strftime(current, '%m'))
        anio=int(datetime.strftime(current, '%Y'))
        hoy_1=datetime(anio,mes,dia,0,0,1)
        hoy_2=datetime(anio,mes,dia,23,59,59)
        hoy_1=hoy_1+timedelta(hours=6)
        hoy_2=hoy_2+timedelta(hours=6)
        pagos=self.env['account.payment'].search(['&',('cierre_id','=',self.id),('payment_type','=','inbound')])
        for pago in pagos:
            movelinereconcilied =self.env['account.move.line'].search([('payment_id','=', pago.id),('full_reconcile_id', '!=', False)])
            invoices =self.env['account.move.line'].search([('full_reconcile_id', '=', movelinereconcilied.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.tipo_documento_id.name','!=','Comprobante de Retencón')])
            for r in invoices:
                if r.date != self.fecha_cierre:
                    total += pago.amount
        return total
        
    def get_anticipo(self):
        total = 0.00
        current=self.fecha_cierre
        dia=int(datetime.strftime(current, '%d'))
        mes=int(datetime.strftime(current, '%m'))
        anio=int(datetime.strftime(current, '%Y'))
        hoy_1=datetime(anio,mes,dia,0,0,1)
        hoy_2=datetime(anio,mes,dia,23,59,59)
        hoy_1=hoy_1+timedelta(hours=6)
        hoy_2=hoy_2+timedelta(hours=6)
        pagos=self.env['account.payment'].search(['&',('cierre_id','=',self.id),('payment_type','=','inbound')])
        for pago in pagos:
            movelinereconcilied =self.env['account.move.line'].search([('payment_id','=', pago.id),('full_reconcile_id', '!=', False)])
            invoices =self.env['account.move.line'].search([('full_reconcile_id', '=', movelinereconcilied.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.tipo_documento_id.name','!=','Comprobante de Retencón')])
            if len(invoices)== 0:
                total +=pago.amount
            #for r in invoices:
            #    if r.invoice_date >= hoy_1 and r.invoice_date<= hoy_2:
            #        total += pago.amount
        return total       

    def get_total_devolucion(self):
        total = 0.00
        #movelinereconcilied =self.env['account.move.line'].search([('full_reconcile_id', '!=', False)])
        #invoices =self.env['account.move.line'].search([('full_reconcile_id', '=', movelinereconcilied.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.tipo_documento_id.name','like','Devolución')])
        invoices = self.env['account.move'].search([('payment_state','=','paid'),('tipo_documento_id.name','like','Devolución'),('cierre_id','=',self.id)])
        for r in invoices:
            total += r.move_id.amount_total 
        return total
    def get_total_devo_diario(self,codes):
        totalpago = 0.00
        for item in self.pago_ids:
            for codigo in codes:
                if item.journal_id.code == codigo:
                    movelinereconcilied =self.env['account.move.line'].search([('payment_id','=', item.id),('full_reconcile_id', '!=', False)])
                    invoices =self.env['account.move.line'].search([('full_reconcile_id', '=', movelinereconcilied.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.tipo_documento_id.name','like','Devolución')])
                    for invoice in invoices:
                        totalpago += invoice.move_id.amount_total
        return totalpago
    def get_total_devo_credito(self):
        totalpago = 0.00
        for item in self.factura_ids:
            if item.tipo_documento_id.name == "Devolución":
                totalpago += item.amount_total
        return totalpago
    def get_total_devolucion_cf(self):
        total = 0.00
        #movelinereconcilied =self.env['account.move.line'].search([('full_reconcile_id', '!=', False)])
        #invoices =self.env['account.move.line'].search([('full_reconcile_id', '=', movelinereconcilied.full_reconcile_id.id),('x_doc_numero','!=', False),('move_id.tipo_documento_id.name','like','Devolución')])
        invoices = self.env['account.move'].search([('state','=','cancel'),('tipo_documento_id.codigo','like','Factura'),('cierre_id','=',self.id)])
        for r in invoices:
            total += r.move_id.amount_total 
        return total



