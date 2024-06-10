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

    #iniciando el envio de objeto completo
    def get_resumen(self):
        resumen = {}
        resumen1 = self.get_resume()
        lineresume = False
        for resumeitem in resumen1:
            lineresume = resumeitem
        grupos = []
        #primera face
        resumen['totalventas'] = self.total_facturado
        resumen['ventacontado'] = lineresume.get('ventacontado')
        resumen['ventacredito'] = lineresume.get('ventacredito')
        resumen['ventascontraentrega'] = 0
        #fin primera fase
        #inicio ingreso de ventas al contado
        resumen['totalingreso'] = 0
        resumen['totalabono'] =0
        resumen['ingreanticipocliente']= lineresume.get('anticipo')
        resumen['aboanticipocliente']= 0
        resumen['ingrechequerecibido'] = lineresume.get('chequesrecibidos')#a
        resumen['abonchequerecibido'] =0 #b
        resumen['ingreefectivo'] = lineresume.get('efectivo') #c
        resumen['aboefectivo'] = 0 #d
        resumen['ingrenacuenta'] = lineresume.get('ncuneta')
        resumen['abonacuenta'] = 0
        resumen['ingretarjetacredito'] = lineresume.get('tarjeta') #f
        resumen['abotarjetacredito'] = 0 #g
        resumen['ingrepayphone'] = 0 #h
        resumen['abopayphone'] = 0#i
        resumen['ingrewompy'] = 0
        resumen['abowompy'] = 0
        resumen['ingreotro'] = 0
        resumen['abootro'] = 0
        #fin ingreso de ventas al contado
        #inicio devouciones
        resumen['totadevoluciones'] = lineresume.get('devoluciones')
        resumen['totalcontado'] = 0
        resumen['efectivo'] = 0
        resumen['cheque'] = 0
        resumen['tarjeta'] =0
        resumen['totalcredito'] = 0
        resumen['notascredito'] = 0
        resumen['devolucionfc'] = 0
        #final de devoluciones
        #inicio totalcomprovanteretencion
        resumen['comprotiva'] = 0
        resumen['comprotivaretenido'] = 0
        resumen['comprototal'] = 0 #e
        #final total comprovante retencion
        #inicio notas de cargo
        resumen['notatotal'] =0
        resumen['notacefectivo'] =0#j
        resumen['notaccheque'] =0#k
        resumen['notactarjeta'] = 0 #l
        resumen['notaotros']=0 #m
        #final notas de cargo
        #inicio de agrupacion de documentos
        resumen['consumidoresfinales'] ={}
        resumen['devoluciones'] = {}
        resumen['ccfs'] = {}
        resumen['notacredito'] = {}
        resumen['notasabono'] = {}
        resumen['comprovantesrete'] = {}
        resumen['notascargo'] = {}
        grupos = self.get_grupos()
        #final de documentos agrupados
        #inicio total a remesar 
        resumen['totalremesar'] = 0
        resumen['remesacheques'] = resumen['ingrechequerecibido']+ resumen['abonchequerecibido']+resumen['notaccheque']# a+b+k
        resumen['remeefectivo'] = resumen['ingrenacuenta']+resumen['ingrechequerecibido']+resumen['aboefectivo']-resumen['comprototal']-resumen['notacefectivo']# a+d-e-j
        resumen['remetarjetacredito'] = resumen['ingretarjetacredito']+resumen['abotarjetacredito']- resumen['notactarjeta'] # f+g-l
        resumen['remepayphone'] = resumen['ingrepayphone']+resumen['abopayphone'] # h+i
        resumen['remewhompy'] = resumen['abowompy']+resumen['ingreotro'] # j + k
        #final total a remesar
        
        
        invoices = []
        comprovanteretencion = []
        for r in self.cierrepago_ids:
            invoice = {}
            invoice['name'] = r.name
            invoice['valor'] = self.get_invoices(r.journal_id.code)
            invoices.append(invoice)
            comprovante = {}
            comprovante['name'] = r.name
            comprovante['valor'] = self.get_compro_retencion
            comprovanteretencion.append(comprovante)
        invoicescredito = {}
        invoicescredito = self.env['account.move'].search([('cierre_id','=',self.id), ('payment_state','not in', ('paid','cancel')), ('state', '=', 'post')])
        devoluciones = []
        devoluciones = self.env['account.move'].search([('cierre_id','=',self.id), ('payment_state','in', ('paid','cancel')),('state', '=', 'post')])
        data = {}
        data['resumen'] =resumen
        data['invoices'] = invoices
        data['invoicescredito'] =invoicescredito
        data['comprovanteretencion'] = comprovanteretencion
        data['devoluciones'] = devoluciones
        data['grupos'] = grupos
        return data
        

 
    #final envio de objeto completo
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
    def get_totalventa(self) :
        totalventa = 0.00
        facturas=self.env['account.move'].search([('cierre_id','=',self.id)])
        for factura in facturas:
            totalventa += factura.amount_total
        return totalventa
    def get_ventastotal(self, contado = 1):
        totalcontado = 0.00
        if contado ==1:
            facturas=self.env['account.move'].search(['&','&','|',('cierre_id','=',self.id),('invoice_payment_term_id','=', 1),('payment_state','=', 'paid'),('invoice_payment_term_id','=', False)])
        else:
            facturas=self.env['account.move'].search([('cierre_id','=',self.id),('invoice_payment_term_id','!=', 1),('payment_state','!=', 'paid')])
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
    def get_grupos(self):
        facturas = []
        #agrupando
        groups=self.env['account.move'].read_group([('cierre_id','=',self.id),('move_type','in',['out_invoice','out_refund']),('state','!=','draft'),('state','!=','cancel'),('caja_id','=',self.caja_id.id)],['tipo_documento_id','min_doc:min(doc_numero)','max_doc:max(doc_numero)','count_doc:count(doc_numero)'],['tipo_documento_id'])            
        for r in groups:                
            doc={}
            tipo=self.env['odoosv.fiscal.document'].browse(r['tipo_documento_id'][0])    
            doc['name']=tipo.name
            doc['min_doc']=r['min_doc']
            doc['max_doc']=r['max_doc']
            doc['cantidad']=r['count_doc']
            anulados=self.env['account.move'].search([('cierre_id','=',self.id),('move_type','in',['out_invoice','out_refund']),('tipo_documento_id', '=', tipo.id),('state','=','cancel')])
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
    def get_compro_retencion(self, diario):
        data = {}
        sql = """
        select 
aj.name  mpago,
aj.code as codigo,
ofd.name,
-- deve ir pago asociado
rp.name as partner,
am2.doc_numero,
-- codigo del empleado
-- nombre del gestor
am2.amount_untaxed as subtotal,
 (Select coalesce(sum(ait.credit-ait.debit),0.00)
       from account_move_line ait 
 	       inner join account_tax atx on ait.tax_line_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where ait.move_id=am2.id
	       and lower(atg.code)='iva'
       ) as Iva,
 (Select coalesce(sum(ait.debit-ait.credit),0.00)
       from account_move_line ait 
 	       inner join account_tax atx on ait.tax_line_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where ait.move_id=am2.id
	       and lower(atg.code)='retencion'
       ) as Retenido,
(Select coalesce(sum(ait.credit-ait.debit),0.00)
       from account_move_line ait 
 	       inner join account_tax atx on ait.tax_line_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where ait.move_id=am2.id
	       and lower(atg.code)='percepcion'
       ) as Percibido,
       am2.amount_total
from account_payment ap
inner join account_payment_method apm on ap.payment_method_id = apm.id 
inner join account_move am on am.payment_id  = ap.id
inner join account_move_line aml on aml.move_id = am.id
inner join account_full_reconcile afr on afr.id = aml.full_reconcile_id 
inner join account_move_line aml2 on aml2.full_reconcile_id = afr.id 
inner join account_move am2 on aml2.move_id = am2.id 
inner join odoosv_fiscal_document ofd on ofd.id = am2.tipo_documento_id 
inner join res_partner rp on rp.id = am2.partner_id 
inner join account_journal aj on am.journal_id = aj.id
where am.state ='posted' and aml.full_reconcile_id is not null
and ap.cierre_id = {0}
and aj.code = '{1}'
and aml2.x_doc_numero is not null
and ofd.name = 'Comprobante de Retencón'
order by apm.name->>'es_ES', ofd.name, am2.date
        """.format(self.id,diario)
        self._cr.execute(sql)
        if self._cr.description: #Verify whether or not the query generated any tuple before fetching in order to avoid PogrammingError: No results when fetching
            data = self._cr.dictfetchall()
        return data
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
                        totalpago = item.amount
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
            total += r.amount_total 
        return total
    

    def get_invoices(self,diarios):
        data = {}
        sql = """
        select 
aj.name  mpago,
aj.code as codigo,
ofd.name nombrefac,
am2.doc_numero as numero,
-- deve ir pago asociado
rp.name as partner,
-- codigo del empleado
-- nombre del gestor
am2.amount_untaxed as subtotal,
 (Select coalesce(sum(ait.credit-ait.debit),0.00)
       from account_move_line ait 
 	       inner join account_tax atx on ait.tax_line_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where ait.move_id=am2.id
	       and lower(atg.code)='iva'
       ) as Iva,
 (Select coalesce(sum(ait.debit-ait.credit),0.00)
       from account_move_line ait 
 	       inner join account_tax atx on ait.tax_line_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where ait.move_id=am2.id
	       and lower(atg.code)='retencion'
       ) as Retenido,
(Select coalesce(sum(ait.credit-ait.debit),0.00)
       from account_move_line ait 
 	       inner join account_tax atx on ait.tax_line_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where ait.move_id=am2.id
	       and lower(atg.code)='percepcion'
       ) as Percibido,
       am2.amount_total as total
from account_payment ap
inner join account_payment_method apm on ap.payment_method_id = apm.id 
inner join account_move am on am.payment_id  = ap.id
inner join account_move_line aml on aml.move_id = am.id
inner join account_full_reconcile afr on afr.id = aml.full_reconcile_id 
inner join account_move_line aml2 on aml2.full_reconcile_id = afr.id 
inner join account_move am2 on aml2.move_id = am2.id 
inner join odoosv_fiscal_document ofd on ofd.id = am2.tipo_documento_id 
inner join res_partner rp on rp.id = am2.partner_id 
inner join account_journal aj on am.journal_id = aj.id
where am.state ='posted' and aml.full_reconcile_id is not null
and ap.cierre_id = {0}
and aj.code = '{1}'
and aml2.x_doc_numero is not null
order by apm.name->>'es_ES', ofd.name, am2.date
        """.format(self.id,diarios)
        self._cr.execute(sql)
        if self._cr.description: #Verify whether or not the query generated any tuple before fetching in order to avoid PogrammingError: No results when fetching
            data = self._cr.dictfetchall()
        return data

    def get_resume(self):
        data = []
        current=self.fecha_cierre
        dia=int(datetime.strftime(current, '%d'))
        mes=int(datetime.strftime(current, '%m'))
        anio=int(datetime.strftime(current, '%Y'))
        hoy_1=datetime(anio,mes,dia,0,0,1)
        hoy_1=hoy_1+timedelta(hours=6)
        sql = """
select 
(
select coalesce(sum(am.amount_total),0.00) from 
account_move am 
where am.state not in ('cancel','paid','draft') and am.payment_state != 'paid'
and am.cierre_id = {0}
) as faccredito,
(
select coalesce(sum(ap.amount),0.00)
from account_payment ap 
inner join account_move am on am.id = ap.move_id  
where am.state = 'posted' and am.ref is null
and ap.cierre_id = {0}
) as anticipo,
(
select coalesce(sum(ap.amount),0.00 )
from account_payment ap 
inner join account_move am on am.id = ap.move_id 
inner join account_journal aj ON aj.id  = am.journal_id 
where aj.code = 'EFEC1'
and ap.is_reconciled = True
and ap.cierre_id = {0}
) as chequesrecibidos,
(
select coalesce(sum(ap.amount),0.00 )
from account_payment ap 
inner join account_move am on am.id = ap.move_id 
inner join account_journal aj ON aj.id  = am.journal_id 
where aj.code = 'EFEC' 
and ap.is_reconciled = True
and ap.cierre_id = {0}
--('PROME', 'BAC', 'AG542','AG543','HIPOT','HIPO1','CUSCA')
) as efectivo,
(
select coalesce(sum(ap.amount),0.00 )
from account_payment ap 
inner join account_move am on am.id = ap.move_id 
inner join account_journal aj ON aj.id  = am.journal_id 
where aj.code = 'TRANS'
and ap.is_reconciled = True
and ap.cierre_id = {0}
) as ncuneta,
(
select coalesce(sum(ap.amount),0.00 )
from account_payment ap 
inner join account_move am on am.id = ap.move_id 
inner join account_journal aj ON aj.id  = am.journal_id 
where aj.code in ('TRJBA', 'TRJAG', 'TRJCU') 
and ap.is_reconciled = True
and ap.cierre_id = {0}
) as tarjeta,
(
select coalesce(sum(am.amount_total),0.00 ) from 
account_move am 
inner join odoosv_fiscal_document ofd on ofd.id = am.tipo_documento_id
where am.state not in ('cancel','paid','draft') and am.payment_state = 'paid'
and ofd.formato = 'NCREDITO'
and am.cierre_id = {0}
) as devoluciones,
(
select coalesce(sum(am.amount_total),0.00) from 
account_move am 
inner join account_payment_term apt on apt.id = am.invoice_payment_term_id
where am.state not in ('cancel','paid','draft') and am.payment_state != 'paid'
and am.cierre_id = {0}
and lower( apt.name->>'es_ES') like '%pago inmediato%'
) as ventacontado,
(
select coalesce(sum(am.amount_total),0.00) from 
account_move am 
inner join account_payment_term apt on apt.id = am.invoice_payment_term_id
where am.state not in ('cancel','paid','draft') and am.payment_state != 'paid'
and am.cierre_id = {0}
and lower( apt.name->>'es_ES')not like '%pago inmediato%'
) as ventacredito
from account_move amt limit 1
        """.format(self.id)
        self._cr.execute(sql)
        if self._cr.description: #Verify whether or not the query generated any tuple before fetching in order to avoid PogrammingError: No results when fetching
            data = self._cr.dictfetchall()
        return data

