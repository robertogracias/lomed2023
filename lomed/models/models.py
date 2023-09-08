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
from datetime import datetime,timedelta
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,UserError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)


class mrp_process_production(models.Model): 
    _name='mrp.production'   
    _inherit = ['mrp.production','barcodes.barcode_events_mixin']
    picking_id=fields.Many2one(comodel_name='lomed.mrp.picking', string='Picking')
    salida_id=fields.Many2one(comodel_name='lomed.mrp.salida', string='Salida') 
    sale_order=fields.Many2one(comodel_name='sale.order', string='Orden de venta',compute='get_order',store=True)
    no_validar_consumo=fields.Boolean("No Validar consumo")

    @api.depends('origin')
    def get_order(self):
        for r in self:
            if r.origin:
                order=self.env['sale.order'].search([('name','=',r.origin)],limit=1)
                if order:
                    r.sale_order=order.id


    def on_barcode_scanned(self, barcode):
        barcode2=barcode.replace('\'',"-")
        barcode3=barcode2.replace(' ','')
        barcode4=barcode3.strip()
        _logger.info('A BUSCAR:'+barcode4)

        producto = self.env['product.product'].search([('barcode', '=', barcode4)],limit=1)
        if producto:
            #if not self.product_id.x_group_product:
            #    raise UserError('El Producto a fabricar debe tener un grupo establecido')
            #if not producto.x_group_product:
            #    raise UserError('El Producto a descargar debe tener un grupo establecido')
            #if self.product_id.x_group_product.id!=producto.x_group_product.id:
            #    raise UserError('El producto a fabricar y la materia prima deben pertenecer al mismo grupo')
            #creando el movimiento
            if producto.free_qty<=0:
                raise UserError('No hay existencias del producto')
            dic1={}
            dic1['product_id']=producto.id
            dic1['location_id']=self.picking_type_id.default_location_src_id.id
            dic1['location_dest_id']=15
            dic1['company_id']=1
            dic1['date']=datetime.now()
            #dic1['date_expected']=datetime.now()
            dic1['product_uom']=1
            dic1['product_uom_qty']=1
            dic1['state']='confirmed'
            dic1['name']=self.name+' OD/OI'
            dic1['raw_material_production_id']=self.id
            self.env['stock.move'].create(dic1)
        else:
            raise UserError('El producto no esta registrado')

    def _pre_button_mark_done(self):
        productions_to_immediate = self._check_immediate()
        if productions_to_immediate:
            return productions_to_immediate._action_generate_immediate_wizard()

        validar_consumo=True
        for production in self:
            if float_is_zero(production.qty_producing, precision_rounding=production.product_uom_id.rounding):
                raise UserError(_('The quantity to produce must be positive!'))
            if production.move_raw_ids and not any(production.move_raw_ids.mapped('quantity_done')):
                raise UserError(_("You must indicate a non-zero amount consumed for at least one of your components"))
            if production.no_validar_consumo==True:
                validar_consumo=False
        if validar_consumo==True: 
            consumption_issues = self._get_consumption_issues()
            if consumption_issues:
                return self._action_generate_consumption_wizard(consumption_issues)

        quantity_issues = self._get_quantity_produced_issues()
        if quantity_issues:
            return self._action_generate_backorder_wizard(quantity_issues)
        return True



class mrp_produccion(models.Model):
    _name='lomed.mrp.picking'
    _inherit = ['lomed.barcode_events_mixin','mail.thread']
    _description='Picking de Ordenes'
    name=fields.Char("Referencia")
    fecha=fields.Date("Fecha")
    ordenes=fields.One2many(comodel_name='mrp.production',inverse_name='picking_id', string='Ordenes')
    last_orden_id=fields.Many2one(comodel_name='mrp.production',string='Ultima Orden')

    
    def on_barcode_scanned(self, barcode):
        barcode2=barcode.replace('\'',"-")
        barcode3=barcode2.replace(' ','')
        barcode4=barcode3.strip()
        _logger.info('A BUSCAR:'+barcode4)

        orden = self.env['mrp.production'].search([('origin', '=', barcode4)],limit=1)
        if orden:
            if orden.state=='confirmed' or orden.state=='draft':
                orden.write({'picking_id':self.id})
                self.last_orden_id=orden.id
                
            else:
                raise UserError('La orden no esta en estado Borrador y/o Confirmada')
        else:
            raise UserError('La orden no esta registrada')

    
    def abrir_orden(self):
        for r in self:
            compose_form = self.env.ref('mrp.mrp_production_form_view', False)
            ctx = dict(
                default_picking_id=r.id
            )
            return {
                'name': 'Asignacion',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mrp.production',
                'views': [(compose_form.id, 'form')],
                'res_id':r.last_orden_id.id,
                'target': 'current',
                'view_id': 'compose_form.id',
                'flags': {'action_buttons': True},
                'context': ctx
                }

class mrp_proccess_salida(models.Model):
    _name='lomed.mrp.salida'
    _inherit = ['lomed.barcode_events_mixin','mail.thread']
    _description='Salida de Ordenes'
    name=fields.Char("Referencia")
    fecha=fields.Date("Fecha")
    ordenes=fields.One2many(comodel_name='mrp.production',inverse_name='salida_id', string='Ordenes')
    last_orden_id=fields.Many2one(comodel_name='mrp.production',string='Ultima Orden')

    
    def on_barcode_scanned(self, barcode):
        barcode2=barcode.replace('\'',"-")
        barcode3=barcode2.replace(' ','')
        barcode4=barcode3.strip()
        _logger.info('A BUSCAR:'+barcode4)

        orden = self.env['mrp.production'].search([('origin', '=', barcode4)],limit=1)
        if orden:
            if orden.state=='to_close':
                orden.qty_producing=orden.product_qty
                for l in orden.move_raw_ids:
                    if l.state=='cancel':
                        continue
                    l.quantity_done=l.product_uom_qty
                    #l.product_qty=l.product_uom_qty
                orden.no_validar_consumo=True
                orden.button_mark_done()
                if orden.state=='done':
                    orden.write({'salida_id':self.id})
                    self.last_orden_id=orden.id                           
            else:
                raise UserError('La orden no esta en esta completa')
        else:
            raise UserError('La orden no esta registrada')


    def cerrar_orden(self):
        for r in self:
            compose_form = self.env.ref('mrp.mrp_production_form_view', False)
            ctx = dict(              
            )
            return  False;



class mrp_process_workcenter(models.Model): 
    _name='mrp.workcenter'   
    _inherit = ['mrp.workcenter','lomed.barcode_events_mixin']
    last_work_id=fields.Many2one(comodel_name='mrp.workorder',string='Ultima Orden')
    message=fields.Char("Mensaje")
    tipo_proceso=fields.Selection(selection=[
        ('Inicio','Inicio'),
        ('Finalizacion','Finalizacion')],string='Tipo de opeacion')
    orden_ids = fields.One2many('mrp.workorder', 'workcenter_id', string='Ordenes en proceso',
        copy=False, domain=[('state', '!=', 'done'),('state', '!=', 'cancel'),('state', '!=', 'pending')])

    def on_barcode_scanned(self, barcode):
        barcode2=barcode.replace('\'',"-")
        barcode3=barcode2.replace(' ','')
        barcode4=barcode3.strip()
        _logger.info('A BUSCAR:'+barcode4)

        for r in self:
            orden = self.env['mrp.production'].search([('origin', '=', barcode4)],limit=1)
            workorder=None
            if orden:
                wokcenterid=str(self.id).replace('NewId_','')
                workorder=self.env['mrp.workorder'].search([('production_id','=',orden.id),('workcenter_id','=',int(wokcenterid))],limit=1)
                if workorder:
                    if workorder.state=='done':
                        r.write({'last_work_id':None,'message':'La Orden ya finalizo'})
                    elif workorder.state=='pending':
                        r.write({'last_work_id':None,'message':'La orden esta en otra estacion'})
                    elif workorder.state=='cancel':
                        r.write({'last_work_id':None,'message':'La orden fue cancelada'})
                    else:
                        if not workorder.date_planned_start:
                            workorder.date_planned_start=datetime.now() 
                            workorder.date_planned_finished=datetime.now()+ timedelta(minutes=workorder.duration_expected)
                        if r.tipo_proceso=='Inicio':
                            workorder.button_start()
                        if r.tipo_proceso=='Finalizacion':
                            workorder.button_finish()
                        r.write({'last_work_id':workorder.id,'message':''})
                else:
                    raise UserError('No hay workorder')
            else:
                raise UserError('La orden no esta registrada')

    
    def abrir_work(self):
        for r in self:
            compose_form = self.env.ref('lomed.lomed_mrp_workcenter_form', False)
            ctx = dict(
               
            )
            #return {
            #        'name': 'Worcenter',
            #        'type': 'ir.actions.act_window',
            #        'view_type': 'form',
            #        'view_mode': 'form',
            #        'res_model': 'mrp.workcenter',
            #        'views': [(compose_form.id, 'form')],
            #        'res_id':r.id,
            #        'target': 'current',
            #        'view_id': 'compose_form.id',
            #        'flags': {'action_buttons': True},
            #        'context': ctx
            #        }
            return False;


class lomed_work_order(models.Model):
    _inherit='mrp.workorder'
    sale_order=fields.Many2one(comodel_name='sale.order', string='Orden de venta',related='production_id.sale_order')
    partner_id=fields.Many2one(comodel_name='res.partner',string='Cliente',related='sale_order.partner_id')
    paciente=fields.Char(string='Paciente',related='sale_order.paciente')
    tipo_proceso=fields.Selection(selection=[
        ('Montaje','Montaje'),
        ('Terminado','Terminado'),
        ('AR','AR'),
        ('Soldadura','Soldadura'),
        ('Servicios Varios','Servicios Varios'),
        ('Convencional + AR SM','Convencional + AR SM'),
        ('Convencional sin AR SM','Convencional sin AR SM'),
        ('Convencional + AR CM','Convencional + AR CM'),
        ('Convencional sin AR CM','Convencional sin AR CM'),
        ('Digital + AR SM','Digital + AR SM'),
        ('Digital sin AR SM','Digital sin AR SM'),
        ('Digital + AR CM','Digital + AR CM'),
        ('Digital sin AR CM','Digital sin AR CM')],related='sale_order.tipo_proceso',string='Tipo de proceso')

class lomed_partner(models.Model):
    _inherit='res.partner'
    vip=fields.Boolean('Cliente VIP')

class lomed_sale_order(models.Model):
    _inherit='sale.order'
    etiqueta_zpl=fields.Text('Etiqueta ZPL',compute='calcular_etiqueta')
    tipo_proceso=fields.Selection(selection=[
        ('Montaje','Montaje'),
        ('Terminado','Terminado'),
        ('AR','AR'),
        ('Soldadura','Soldadura'),
        ('Servicios Varios','Servicios Varios'),
        ('Convencional + AR SM','Convencional + AR SM'),
        ('Convencional sin AR SM','Convencional sin AR SM'),
        ('Convencional + AR CM','Convencional + AR CM'),
        ('Convencional sin AR CM','Convencional sin AR CM'),
        ('Digital + AR SM','Digital + AR SM'),
        ('Digital sin AR SM','Digital sin AR SM'),
        ('Digital + AR CM','Digital + AR CM'),
        ('Digital sin AR CM','Digital sin AR CM')])
    paciente=fields.Char("Paciente")

    def imprimir_label(self):
        x=0
        for r in self:
            x=1

    def calcular_etiqueta(self):
        for r in self:
            anti=''
            paciente=''
            dia=''
            cliente=''
            fechaatomar=r.date_order
            if not fechaatomar:
                fechaatomar=r.create_date
            if fechaatomar:
                fecha=fechaatomar and fechaatomar+timedelta(hours=-6) or None
                fulldate=fecha.strftime("%d-%m-%Y, %H:%M:%S")
                dia=fechaatomar and fecha.strftime('%A') or ''
                if dia=='Monday':
                    dia='LU'
                if dia=='Tuesday':
                    dia='MA'
                if dia=='Wednesday':
                    dia='MI'
                if dia=='Thursday':
                    dia='JU'
                if dia=='Friday':
                    dia='VI'
                if dia=='Saturday':
                    dia='SA'
                if dia=='Sunday':
                    dia="DO"
                anti=''
                horas=96
                if r.partner_id.vip==True:
                    horas=24
                else:
                    if r.tipo_proceso=='Montaje':
                        horas=24
                    if r.tipo_proceso=='Terminado':
                        horas=24
                    if r.tipo_proceso=='AR':
                        horas=24
                    if r.tipo_proceso=='Soldadura':
                        horas=24
                    if r.tipo_proceso=='Servicios Varios':
                        horas=96
                    if r.tipo_proceso=='Convencional + AR SM':
                        horas=72
                    if r.tipo_proceso=='Convencional sin AR SM':
                        horas=48
                    if r.tipo_proceso=='Convencional + AR CM':
                        horas=96
                    if r.tipo_proceso=='Convencional sin AR CM':
                        horas=72
                    if r.tipo_proceso=='Digital + AR SM':
                        horas=72
                    if r.tipo_proceso=='Digital sin AR SM':
                        horas=48
                    if r.tipo_proceso=='Digital + AR CM':
                        horas=96
                    if r.tipo_proceso=='Digital sin AR CM':
                        horas=72
                entrega=fecha+timedelta(hours=horas)
                entregastr=entrega.strftime("%d%m")
                for l in r.order_line:
                    if l.product_id.id==55264:
                        anti='A'
                    if l.product_id.id==50937:
                        anti='A'
                    if l.product_id.id==75982:
                        anti='A'
                paciente=''
                if r.paciente:
                    paciente=r.paciente
                cliente=r.partner_id.name
                if len(cliente)>30:
                    cliente=cliente[0:30]
                r.etiqueta_zpl = '^XA ^CF01,13,30 ^FO5,10 ^FWN ^FDLOMED S.A. DE C.V.^FS ^FO430,10 ^FWN ^FDLOMED S.A. DE C.V.^FS ^CF01,15,25 ^FO5,30 ^FWN ^FD'+cliente+'^FS ^FO430,30 ^FWN ^FD'+cliente+'^FS ^FO5,50 ^FWN ^FD'+paciente+'^FS ^FO430,50 ^FWN ^FD'+paciente+'^FS ^FO5,70 ^FWN ^FDDig:'+r.create_uid.name+'^FS ^FO430,70 ^FWN ^FDDig:'+r.create_uid.name+'^FS ^FO5,85 ^FWN ^FD^FS ^FO430,85 ^FWN ^FD^FS ^FO5,90 ^FWN ^FD'+fulldate+'^FS ^FO430,90 ^FWN ^FD'+fulldate+'^FS ^CF01,40,40 ^FO5,105 ^FWN ^FD'+dia+'^FS ^FO50,105 ^FWN ^FD'+anti+'^FS  ^FO5,147 ^FWN ^FD'+entregastr+'^FS ^FO90,105 ^BY2 ^BCN,60,Y,N,N ^FD'+r.name.upper()+'^FS ^FO430,105 ^FWN ^FD'+dia+'^FS ^FO485,105 ^FWN ^FD'+anti+'^FS ^FO430,147 ^FWN ^FD'+entregastr+'^FS ^FO530,105 ^BY2 ^BCN,60,Y,N,N ^FD'+r.name.upper()+'^FS ^XZ'
