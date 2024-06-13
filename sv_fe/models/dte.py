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
import uuid
from datetime import datetime,timedelta
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)


def numero_to_letras(numero):
    """
    Funciones para convertir las letas a numeros
    """
    indicador = [("",""),("MIL","MIL"),("MILLON","MILLONES"),("MIL","MIL"),("BILLON","BILLONES")]
    entero = int(numero)
    decimal = int(round((numero - entero)*100))
    #print 'decimal : ',decimal 
    contador = 0
    numero_letras = ""
    _logger.info('ENTERO:'+str(entero))
    while entero >0:
        a = entero % 1000
        if contador == 0:
            en_letras = convierte_cifra(a,1).strip()
            _logger.info('letras 1:'+en_letras)
        else :
            en_letras = convierte_cifra(a,0).strip()
            _logger.info('letras 2:'+en_letras)
        if a==0:
            numero_letras = en_letras+" "+numero_letras
            _logger.info('letras 3:'+numero_letras)
        elif a==1:
            if contador in (1,3):
                numero_letras = indicador[contador][0]+" "+numero_letras
                _logger.info('letras 4:'+numero_letras)
            else:
                numero_letras = en_letras+" "+indicador[contador][0]+" "+numero_letras
                _logger.info('letras 5:'+numero_letras)
        else:
            numero_letras = en_letras+" "+indicador[contador][1]+" "+numero_letras
            _logger.info('letras 6:'+numero_letras)
        numero_letras = numero_letras.strip()
        contador = contador + 1
        entero = int(entero / 1000)
    numero_letras = numero_letras+" CON " + (str(decimal) if decimal>=10 else ('0'+str(decimal))) +"/100"
    return numero_letras
 

def convierte_cifra(numero,sw):
    lista_centana = ["",("CIEN","CIENTO"),"DOSCIENTOS","TRESCIENTOS","CUATROCIENTOS","QUINIENTOS","SEISCIENTOS","SETECIENTOS","OCHOCIENTOS","NOVECIENTOS"]
    lista_decena = ["",("DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISEIS","DIECISIETE","DIECIOCHO","DIECINUEVE"),
                    ("VEINTE","VEINTIUNO","VEINTIDOS","VEINTITRES","VEINTICUATRO","VEINTICINCO","VEINTISEIS","VEINTISIETE","VEINTIOCHO","VEINTINUEVE")
                    ,("TREINTA","TREINTA Y "),("CUARENTA" , "CUARENTA Y "),
                    ("CINCUENTA" , "CINCUENTA Y "),("SESENTA" , "SESENTA Y "),
                    ("SETENTA" , "SETENTA Y "),("OCHENTA" , "OCHENTA Y "),
                    ("NOVENTA" , "NOVENTA Y ")
                ]
    lista_unidad = ["",("UN" , "UNO"),"DOS","TRES","CUATRO","CINCO","SEIS","SIETE","OCHO","NUEVE"]
    centena = int (numero / 100)
    decena = int((numero -(centena * 100))/10)
    unidad = int(numero - (centena * 100 + decena * 10))
    #print "centena: ",centena, "decena: ",decena,'unidad: ',unidad
    texto_centena = ""
    texto_decena = ""
    texto_unidad = ""
    #Validad las centenas
    texto_centena = lista_centana[centena]
    if centena == 1:
        if (decena + unidad)!=0:
            texto_centena = texto_centena[1]
        else :
            texto_centena = texto_centena[0]
    #Valida las decenas
    texto_decena = lista_decena[decena]
    if ((decena == 1) or (decena == 2)):
         texto_decena = texto_decena[unidad]
    elif decena > 2 :
        if unidad != 0 :
            texto_decena = texto_decena[1]
        else:
            texto_decena = texto_decena[0]
    #Validar las unidades
    #print "texto_unidad: ",texto_unidad
    if decena != 1:
        texto_unidad = lista_unidad[unidad]
        if unidad == 1:
            texto_unidad = texto_unidad[sw]
    return "%s %s %s" %(texto_centena,texto_decena,texto_unidad)


def calculo_letras(campo):
    cadena = list(campo)
    a = []
    for record in cadena: 
        if record=='0':
            a.append('cero')
        if record=='1':
            a.append('uno')
        if record=='2':
            a.append('dos')
        if record=='3':
            a.append('tres')
        if record=='4':
            a.append('cuatro')
        if record=='5':
            a.append('cinco')
        if record=='6':
            a.append('seis')
        if record=='7':
            a.append('siete')
        if record=='8':
            a.append('ocho')
        if record=='9':
            a.append('nueve')
        if record=='-':
            a.append('-')
            
    str1  = ' '.join(a)
    return str1

class sv_fe_contingencia(models.Model):
    _name='sv_fe.contingencia_ocurrencia'
    doc_json=fields.Text("Doc JSON",copy=False)
    doc_firmado=fields.Text("Doc. Firmado",copy=False)
    doc_sellado=fields.Text("Doc. Sellado",copy=False)
    doc_respuesta=fields.Text("Respuesta",copy=False)
    company_id=fields.Many2one(comodel_name='res.company',string="Empresa")
    uuid=fields.Char("Codigo de Generacion",copy=False)
    sello=fields.Char("Sello",copy=False)
    control=fields.Char("Numero de control",copy=False)

    responsable=fields.Char("Responsable")
    responsable_doc=fields.Char("Numero de documento")
    responsable_tel=fields.Char("Numero de telefono")
    fecha=fields.Datetime("Fecha")

    #Motivo
    fecha1=fields.Datetime("Inicio")
    fecha2=fields.Datetime("Finalizacion")
    motivo=fields.Char("Motivo")
    name=fields.Char("NUMERO")
    dte_estado=fields.Char("Estado del DTE")

    fe_contingencia_id=fields.Many2one(comodel_name='sv_fe.contingencia',string='Tipo de contingencia')
    
    #documentos
    dte_ids=fields.Many2many(comodel_name="account.move",string="DTEs")


    def get_name(self):
        for r in self:
            if r.control:
                r.name=r.control
            else:
                r.name='-'
    
    def send_dtes(self):
        self.ensure_one()
        for d in self.dte_ids:
            if not d.sello:
                d.generar_fe(self)



    def contingencia_fe(self):
        self.ensure_one()
        f=self
        firma={}
        firma['nit']=f.dte_ids.company_id.partner_id.nit.replace('-','')
        firma['passwordPri']=f.dte_ids.company_id.fe_ambiente_id.llave_privada
        firma['dteJson']=f.get_contigencia()       
        f.doc_json=firma['dteJson']
        encabezado = {"content-type": "application/JSON","User-Agent":"Odoo/16"}
        json_datos = json.dumps(firma)
        json_datos=json_datos.replace('None','null')
        json_datos=json_datos.replace('False','null')
        #raise UserError(json_datos)
        result = requests.post(f.dte_ids.company_id.fe_ambiente_id.firmador,data=json_datos, headers=encabezado)
        respuesta=json.loads(result.text)
        #raise UserError(result.text)
        if respuesta['status']=="OK":
            body=respuesta["body"]
            f.doc_firmado=body
            encabezado={}
            encabezado['Authorization']=f.dte_ids.company_id.fe_ambiente_id.get_token()
            encabezado['User-Agent']="Odoo/16"
            encabezado['content-type']="application/JSON"
            dic={}
            dic['ambiente']=f.dte_ids.company_id.fe_ambiente_id.codigo
            dic['idEnvio']=f.id+100000
            dic['version']=2
            #dic['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
            dic['documento']=body
            dic['codigoGeneracion']=f.uuid
            json_datos = json.dumps(dic)
            json_datos=json_datos.replace('None','null')
            json_datos=json_datos.replace('False','null')
            #raise UserError(str(encabezado)+'------'+json_datos)
            result=requests.post(f.dte_ids.company_id.fe_ambiente_id.url+'/fesv/contingencia',data=json_datos, headers=encabezado)
            f.doc_respuesta=result.text
            respuesta=json.loads(result.text)
            f.dte_estado=respuesta['estado']
            if respuesta['estado']=='RECIBIDO':
                f.sello=respuesta['selloRecibido']
            else:
                f.dte_error=respuesta['observaciones']
            #raise UserError(result.text)
        #raise UserError(result.text)


##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   Contingencia
##-----------------------------------------------------------------------------------------------------------------------------------------------------------
    def get_contigencia(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_ct()
        dic['emisor']=f.get_emisor_ct()
        dic['detalleDTE']=f.get_documento_ct()
        dic['motivo']=f.get_motivo_ct()

       
        return dic



    def get_emisor_ct(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['nombreResponsable']=f.responsable
        emisor['tipoDocResponsable']='13'
        emisor['numeroDocResponsable']=f.responsable_doc
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['telefono']=f.company_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codEstableMH']=None
        #emisor['codEstable']=None
        #emisor['codPuntoVentaMH']=None
        emisor['codPuntoVenta']=None
        return emisor

    def get_identificacion_ct(self):        
        self.ensure_one()
        f=self
        #if not f.dte_ids.reversion_uuid:
        #    f.dte_ids.reversion_uuid=str(uuid.uuid4()).upper()
        identificacion={}
        identificacion['version']=3
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        if not f.uuid:
            f.uuid=str(uuid.uuid4()).upper()
            f.control=self.env['ir.sequence'].next_by_code('fe.contingencia')
            f.name=f.control
        identificacion['codigoGeneracion']=f.uuid
        fecha=datetime.now()+timedelta(hours=-6)
        identificacion['fTransmision']=fecha.strftime('%Y-%m-%d')
        identificacion['hTransmision']=fecha.strftime('%H:%M:%S')
        return identificacion

    
    def get_documento_ct(self):
        self.ensure_one()
        f=self
        dic={}
        lista=[]
        i=0
        for d in f.dte_ids:
            dic={}
            i+=1
            dic['noItem']=i
            dic['codigoGeneracion']=d.uuid
            dic['tipoDoc']=d.tipo_documento_id.fe_tipo_doc_id.codigo
            lista.append(dic)
        
        return lista
    

    def get_motivo_ct(self):
        self.ensure_one()
        f=self
        dic={}
        dic['fInicio']=f.fecha1.strftime('%Y-%m-%d')
        dic['fFin']=f.fecha2.strftime('%Y-%m-%d')
        dic['hInicio']=f.fecha1.strftime('%H:%M:%S')
        dic['hFin']=f.fecha2.strftime('%H:%M:%S')
        dic['tipoContingencia']=int(f.fe_contingencia_id.codigo)
        dic['motivoContingencia']=f.fe_contingencia_id.name
     
        
        return dic

class sv_fe_donacion_doc(models.Model):
    _name='sv_fe.donacion_doc'
    name=fields.Char("Identificacion")
    descripcion=fields.Char("Detalle")
    fe_doc_asociado_id=fields.Many2one(comodel_name='sv_fe.docasociado',string="Documento Asociado")
    move_id=fields.Many2one(comodel_name='account.move',string='Factura')
       


class sv_fe_move(models.Model):
    _inherit='account.move'
    uuid=fields.Char("Codigo de Generacion",copy=False)
    sello=fields.Char("Sello",copy=False)
    control=fields.Char("Numero de control",copy=False)

    reversion_sello=fields.Char("Sello",copy=False)
    reversion_uuid=fields.Char("UUID",copy=False)

    date_confirm=fields.Datetime('Fecha de confirmacion',copy=False)

    gravadas=fields.Float("Ventas Gravadas",copy=False)
    exentas=fields.Float("Ventas Exentas",copy=False)
    nosujetas=fields.Float("Ventas No Sujetas",copy=False)
    
    gravadas_des=fields.Float("Descuento Gravado ",copy=False)
    exentas_des=fields.Float("Descuento Exento",copy=False)
    nosujetas_des=fields.Float("Descuento Exento",copy=False)

    gravadas_linea_des=fields.Float("Descuento lineas Gravado ",copy=False)
    exentas_linea_des=fields.Float("Descuento lineas Exento",copy=False)
    nosujetas_linea_des=fields.Float("Descuento lineas Exento",copy=False)
    
    retencion=fields.Float("Retencion",copy=False)
    percepcion=fields.Float("Percepcion",copy=False)
    isr=fields.Float("ISR",copy=False)
    iva=fields.Float("IVA",copy=False)
    iva_des=fields.Float("IVA Desc.",copy=False)

    entrega=fields.Char("Entrega",copy=False)
    doc_entrega=fields.Char("Doc. Entrega",copy=False)
    recibe=fields.Char("Recibe",copy=False)
    doc_recibe=fields.Char("Doc. Recibe",copy=False)
    observaciones=fields.Char("Observaciones",copy=False)
    placa=fields.Char("Placa Vehiculo",copy=False)

    doc_json=fields.Text("Doc JSON",copy=False)
    doc_firmado=fields.Text("Doc. Firmado",copy=False)
    doc_sellado=fields.Text("Doc. Sellado",copy=False)
    doc_respuesta=fields.Text("Respuesta",copy=False)

    reversion_json=fields.Text("Doc JSON",copy=False)
    reversion_firmado=fields.Text("Doc. Firmado",copy=False)
    reversion_sellado=fields.Text("Doc. Sellado",copy=False)
    reversion_respuesta=fields.Text("Reversión respuesta",copy=False)
    reversion_motivo=fields.Char("Motivo",copy=False)
    reversion_responsable=fields.Char("Responsable",copy=False)
   
    reversion_responsable_tipo=fields.Char('Tipo de documento Responsable',copy=False)
    reversion_responsable_doc=fields.Char("Doc del Responsable",copy=False)
    reversion_solicita=fields.Char("Nombre solicitante",copy=False)
    reversion_solicita_tipo=fields.Char("Tipo Doc solicitante",copy=False)
    
    reversion_solicita_doc=fields.Char("Doc solicitante",copy=False)
    sv_fe_tipo_itemexpor_id=fields.Many2one(comodel_name='sv_fe.tipo_item', string='Tipo item Exportacion')
    sv_fe_resinto_id=fields.Many2one(comodel_name='sv_fe.resinto',string='Recinto fiscal')
    flete=fields.Float('Flete')
    sv_fe_regimen_id=fields.Many2one(comodel_name='sv_fe.regimen', string='Regimen')
    sv_fe_seguro=fields.Float('Costo del seguro')
    reversion_responsable_tipo_id=fields.Many2one(comodel_name='sv_fe.doc_identificacion',string='Tipo documento')
    reversion_solicita_tipo_id=fields.Many2one(comodel_name='sv_fe.doc_identificacion',string='Tipo documento')
    doc_relacionado=fields.Many2one(comodel_name='account.move',string='Documento relacionado',copy=False)
    dte_estado=fields.Char("Estado del DTE",copy=False)
    dte_error=fields.Char("Error del DTE",copy=False)
    dte_qr=fields.Char(string='QR',compute='get_qr',store=False)
    fe_tipo_doc_id=fields.Many2one(comodel_name='sv_fe.tipo_doc',related='tipo_documento_id.fe_tipo_doc_id',store=True,string="Tipo de documento")
    fe_codigo=fields.Char(string='Codigo tipo doc',related='fe_tipo_doc_id.codigo',store=True)
    fe_transmision_id=fields.Many2one(comodel_name='sv_fe.transmision',string='Modelo de Transmision')
    fe_ambiente_id=fields.Many2one(comodel_name='sv_fe.ambiente',string='Ambiente')
    proforma=fields.Boolean("Proforma")
    contingencia=fields.Many2one(comodel_name='sv_fe.contingencia_ocurrencia',string='Contingencia')
    sv_fe_transporte_id=fields.Many2one(comodel_name='sv_fe.transporte',string='Transporte')
    doc_asociados=fields.One2many(comodel_name='sv_fe.donacion_doc',string='Documentos asociados',inverse_name='move_id')

    extra_discount=fields.Monetary("Descuento extra")
    permite_factura_rectificativa=fields.Boolean(string='Permite facturac rectificativa',related='tipo_documento_id.permite_factura_rectificativa',store=True)
    permite_reversion=fields.Boolean(string="Permite Reversion",compute="get_allow_reversion",store=False)



    

    @api.depends('date_confirm','tipo_documento_id')
    def get_allow_reversion(self):
        for r in self:
            resultado=True
            if r.tipo_documento_id:
                if r.tipo_documento_id.horas_reversion>0 and r.date_confirm:
                    data1 = r.date_confirm
                    data2 = datetime.now()
                    diff = data2 - data1
                    days, seconds = diff.days, diff.seconds
                    hours = days * 24 + seconds // 3600
                    if hours<=r.tipo_documento_id.horas_reversion:
                        resultado= True
                    else:
                        resultado= False
            r.permite_reversion=resultado

    def action_reverse(self):
        for r in self:
            if r.move_type=='out_invoice':
                if r.tipo_documento_id and not r.tipo_documento_id.permite_factura_rectificativa:
                    raise UserError('ESTE TIPO DE DOCUMENTO NO PERMITE NOTA DE CREDITO')
        res=super(sv_fe_move,self).action_reverse()
        return res;


    def button_draft(self):
        res=super(sv_fe_move,self).button_draft()
        for r in self:
            if r.sello:
                raise UserError("EL DTE YA FUE TRANSMITIDO Y SELLADO")

        

    def get_json(self):
        for r in self:
            return json.loads(r.doc_json)

    @api.depends('sello','dte_estado')
    def get_qr(self):
        for r in self:
            res=''
            if r.move_type in ('out_invoice','out_refund','in_invoice','in_refound'):
                ambiente='00'
                if r.fe_ambiente_id:
                    ambiente=r.fe_ambiente_id.codigo
                else:
                    ambiente=r.company_id.fe_ambiente_id.codigo
                if r.uuid:
                    res='https://admin.factura.gob.sv/consultaPublica%3Fambiente='+ambiente+'%26codGen='+r.uuid+'%26fechaEmi='+(r.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
                else:
                    res='https://admin.factura.gob.sv/consultaPublica%3Fambiente='+ambiente+'%26codGen='+'proforma'+'%26fechaEmi='+(datetime.now()+timedelta(hours=-6)).strftime('%Y-%m-%d')
                #res='https://admin.factura.gob.sv/consultaPublica?ambiente=01&codGen='+r.uuid+'&echaEmi='+(r.date_confirm).strftime('%Y-%m-%d')
            r.dte_qr=res

    def contingencia_fes(self):
        self.env['sv_fe.contingencia_ocurrencia'].contingencia_fe()


    def solo_imprimir(self):
        self.ensure_one()
        self.generar_solo_fe()
        return self.env.ref('sv_fe.dte_report').report_action(self)

    def generar_solo_fe(self):
        self.ensure_one()
        f=self
        
        #generando el dte
        #dte=str(f.get_factura())
        #dte=dte.replace('None','null')
        #dte=dte.replace('False','null')
        #dte=dte.replace('\'','\"')
        #firmandolo
        if f.sello:
            raise UserError('EL DTE YA FUE TRANSMITIDO')
        f.proforma=True
        #f.date_confirm=datetime.now()
        firma={}
        firma['nit']=f.company_id.partner_id.nit.replace('-','')
        firma['passwordPri']=f.company_id.fe_ambiente_id.llave_privada
        if f.tipo_documento_id.fe_tipo_doc_id.codigo=='01':
            firma['dteJson']=f.get_factura()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='03':
            firma['dteJson']=f.get_ccf()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='05':
            firma['dteJson']=f.get_nc()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='06':
            firma['dteJson']=f.get_nd()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='14':
            firma['dteJson']=f.get_se()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='07':
            firma['dteJson']=f.get_cr()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='11':
            firma['dteJson'] = f.get_exp()
        else:
            raise UserError('No ha configurado el tipo de documento para que pueda emitir una factura electrónica.')
        #if f.fe_tipo_doc_id.oveeride_doc:
        #    f.doc_numero=f.control
        encabezado = {"content-type": "application/JSON","User-Agent":"Odoo/16"}
        json_datos = json.dumps(firma)
        json_datos=json_datos.replace('None','null')
        json_datos=json_datos.replace('False','null')
        json_datos=json_datos.replace('false','null')
        json_datos_cliente=json.dumps( firma['dteJson'])
        json_datos_cliente=json_datos_cliente.replace('None','null')
        json_datos_cliente=json_datos_cliente.replace('False','null')
        json_datos_cliente=json_datos_cliente.replace('false','null')
        f.doc_json=json_datos_cliente

        
    def generar_fe(self,contingencia=None):
        self.ensure_one()
        f=self
        f.proforma=False
        #raise UserError(str(contingencia))
        if not contingencia:
            f.fe_transmision_id=self.env.ref('sv_fe.svfe_transmision_1').id
            f.fe_ambiente_id=f.company_id.fe_ambiente_id.id
        else:
            f.fe_transmision_id=self.env.ref('sv_fe.svfe_transmision_2').id
            f.contingencia=contingencia.id

        #generando el dte
        #dte=str(f.get_factura())
        #dte=dte.replace('None','null')
        #dte=dte.replace('False','null')
        #dte=dte.replace('\'','\"')
        #firmandolo
        dic={}
        dic['move']=f
        dic['partner']=f.partner_id
        dic['ValidationError']=ValidationError
        if f.tipo_documento_id.validacion_previa:
            safe_eval(r.tipo_documento_id.validacion_previa,dic, mode='exec')
        if not f.date_confirm:
            f.date_confirm=datetime.now()
        firma={}
        firma['nit']=f.company_id.partner_id.nit.replace('-','')
        firma['passwordPri']=f.company_id.fe_ambiente_id.llave_privada
        if f.tipo_documento_id.fe_tipo_doc_id.codigo=='01':
            firma['dteJson']=f.get_factura()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='03':
            firma['dteJson']=f.get_ccf()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='05':
            firma['dteJson']=f.get_nc()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='06':
            firma['dteJson']=f.get_nd()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='14':
            firma['dteJson']=f.get_se()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='07':
            firma['dteJson']=f.get_cr()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='11':
            firma['dteJson'] = f.get_exp()
        elif f.tipo_documento_id.fe_tipo_doc_id.codigo=='15':
            firma['dteJson'] = f.get_donacion()
        else:
            raise UserError('No ha configurado el tipo de documento para que pueda emitir una factura electrónica.')
        if f.tipo_documento_id.override_doc:
            f.doc_numero=f.control
    
        encabezado = {"content-type": "application/JSON","User-Agent":"Odoo/16"}
        json_datos = json.dumps(firma)
        json_datos=json_datos.replace('None','null')
        json_datos=json_datos.replace('False','null')
        json_datos=json_datos.replace('false','null')
        json_datos_cliente=json.dumps( firma['dteJson'])
        json_datos_cliente=json_datos_cliente.replace('None','null')
        json_datos_cliente=json_datos_cliente.replace('False','null')
        json_datos_cliente=json_datos_cliente.replace('false','null')
        f.doc_json=json_datos_cliente
        #raise UserError(json_datos)
        self.env.cr.savepoint()
        result = requests.post(f.company_id.fe_ambiente_id.firmador,data=json_datos, headers=encabezado)
        respuesta=json.loads(result.text)
        #raise UserError(result.text)
        if respuesta['status']=="OK":
            body=respuesta["body"]
            f.doc_firmado=body
            encabezado={}
            encabezado['Authorization']=f.company_id.fe_ambiente_id.get_token()
            encabezado['User-Agent']="Odoo/16"
            encabezado['content-type']="application/JSON"
            dic={}
            dic['ambiente']=f.company_id.fe_ambiente_id.codigo
            dic['idEnvio']=f.id
            dic['version']=f.tipo_documento_id.version
            dic['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
            dic['documento']=body
            dic['codigoGeneracion']=f.uuid
            json_datos = json.dumps(dic)
            json_datos=json_datos.replace('None','null')
            json_datos=json_datos.replace('False','null')
            #raise UserError(str(encabezado)+'------'+json_datos)
            print('---------------------------------------------------------------------------------------------------------')
            print(str(encabezado))
            print('------------------------------')
            print(str(json_datos))
            print('----------------------------------------------------------------------------------------------------------')
            self.env.cr.savepoint()
            try:
                result=requests.post(f.company_id.fe_ambiente_id.url+'/fesv/recepciondte',data=json_datos, headers=encabezado)
            except:
                raise UserError('EL SITIO DEL MH NO ESTA EN LINEA')
            print(str(result))
            f.doc_respuesta=result.text
            try:
                respuesta=json.loads(result.text)
                f.dte_estado=respuesta['estado']
                if respuesta['estado']=='PROCESADO':
                    f.sello=respuesta['selloRecibido']
                else:
                    f.dte_error=(str(respuesta['observaciones'])+'-'+str(respuesta['descripcionMsg']))
            except:
                print('Error')
            #raise UserError(result.text)
        #raise UserError(result.text)


    def revertir_fe(self):
        self.ensure_one()
        f=self
        firma={}
        firma['nit']=f.company_id.partner_id.nit.replace('-','')
        firma['passwordPri']=f.company_id.fe_ambiente_id.llave_privada
        firma['dteJson']=f.get_reversion()       
        f.reversion_json=firma['dteJson']
        encabezado = {"content-type": "application/JSON","User-Agent":"Odoo/16"}
        json_datos = json.dumps(firma)
        json_datos=json_datos.replace('None','null')
        json_datos=json_datos.replace('False','null')
        #raise UserError(json_datos)
        result = requests.post(f.company_id.fe_ambiente_id.firmador,data=json_datos, headers=encabezado)
        respuesta=json.loads(result.text)
        #raise UserError(result.text)
        if respuesta['status']=="OK":
            body=respuesta["body"]
            f.reversion_firmado=body
            encabezado={}
            encabezado['Authorization']=f.company_id.fe_ambiente_id.get_token()
            encabezado['User-Agent']="Odoo/16"
            encabezado['content-type']="application/JSON"
            dic={}
            dic['ambiente']=f.company_id.fe_ambiente_id.codigo
            dic['idEnvio']=f.id+100000
            dic['version']=2
            dic['documento']=body
            dic['codigoGeneracion']=f.uuid
            json_datos = json.dumps(dic)
            json_datos=json_datos.replace('None','null')
            json_datos=json_datos.replace('False','null')
            print('---------------------------------------------------------------------------------------------------------')
            print(str(encabezado))
            print('------------------------------')
            print(str(json_datos))
            print('----------------------------------------------------------------------------------------------------------')
            #raise UserError(str(encabezado)+'------'+json_datos)
            try:
                result=requests.post(f.company_id.fe_ambiente_id.url+'/fesv/anulardte',data=json_datos, headers=encabezado)
            except:
                raise UserError('EL SITIO DEL MH NO ESTA EN LINEA')
            print(str(result))
            f.reversion_respuesta=result.text
            try:
                respuesta=json.loads(result.text)
                if respuesta['estado']=='PROCESADO':
                    f.dte_estado='INVALIDADO'
                    f.reversion_sello=respuesta['selloRecibido']
            except:
                print('Error')
        else:
            raise UserError(respuesta['status'])

    


##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   Reversion
##-----------------------------------------------------------------------------------------------------------------------------------------------------------
    def get_reversion(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_reve()
        dic['emisor']=f.get_emisor_reve()
        dic['documento']=f.get_documento_reve()
        dic['motivo']=f.get_motivo_reve()
        return dic



    def get_emisor_reve(self):
        self.ensure_one()
        f=self
        emisor={}

        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['nomEstablecimiento']=f.company_id.name
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codEstableMH']=None
        emisor['codEstable']=None
        emisor['codPuntoVentaMH']=None
        emisor['codPuntoVenta']=None
        return emisor

    def get_identificacion_reve(self):        
        self.ensure_one()
        f=self
        if not f.reversion_uuid:
            f.reversion_uuid=str(uuid.uuid4()).upper()
        identificacion={}
        identificacion['version']=2
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['codigoGeneracion']=f.reversion_uuid
        fecha=datetime.now()+timedelta(hours=-6)
        identificacion['fecAnula']=fecha.strftime('%Y-%m-%d')
        identificacion['horAnula']=fecha.strftime('%H:%M:%S')
        return identificacion

    def get_receptor_reve(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            if f.partner_id.nrc and f.partner_id.nrc=='NA':
                receptor['tipoDocumento']='37'
                receptor['numDocumento']=f.partner_id.nit.replace('-','')
                receptor['nrc']=None
            else:
                if f.partner_id.nit and f.tipo_documento_id.codigo != 14:
                    receptor['tipoDocumento']='36'
                    receptor['numDocumento']=f.partner_id.nit.replace('-','')
                elif f.partner_id.dui:
                    receptor['tipoDocumento']='13'
                    receptor['numDocumento']=f.partner_id.dui.replace('-','')
                if f.partner_id.nrc:
                    receptor['nrc']=f.partner_id.nrc
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['correo']=f.partner_id.email
            return receptor
        else:
            return None

    def get_documento_reve(self):
        self.ensure_one()
        f=self
        dic={}
        dic['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        dic['codigoGeneracion']=f.uuid
        dic['selloRecibido']=f.sello
        dic['numeroControl']=f.control
        dic['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
        dic['montoIva']=round(f.iva,2)
        dic['codigoGeneracionR']=None
        if f.partner_id.nrc and f.partner_id.nrc=='NA' or f.tipo_documento_id.fe_tipo_doc_id.codigo == '11':
                if  f.tipo_documento_id.fe_tipo_doc_id.codigo == '11':
                    dic['tipoDocumento']='37'
                    dic['numDocumento']=f.partner_id.nrc.replace('-','')
        else:
            if f.partner_id.nit:
                dic['tipoDocumento']='36'
                dic['numDocumento']=f.partner_id.nit.replace('-','')
            elif f.partner_id.dui:
                dic['tipoDocumento']='13'
                dic['numDocumento']=f.partner_id.dui.replace('-','')
            else:
                dic['tipoDocumento']=''
                dic['numDocumento']=''
        dic['nombre']=f.partner_id.name
        dic['telefono']=f.partner_id.phone
        dic['correo']=f.partner_id.email
        
        return dic
    

    def get_motivo_reve(self):
        self.ensure_one()
        f=self
        dic={}
        if f.tipo_documento_id.fill_reversion:
            if not f.reversion_responsable:
                f.reversion_responsable=self.env.user.partner_id.name
            if not f.reversion_responsable_doc:
                if self.env.user.partner_id.dui:
                    f.reversion_responsable_tipo_id=self.env.ref('sv_fe.svfe_doc_identificacion_2').id
                    f.reversion_responsable_doc=self.env.user.partner_id.dui
                elif self.env.user.partner_id.nit:
                    f.reversion_responsable_tipo_id=self.env.ref('sv_fe.svfe_doc_identificacion_1').id
                    f.reversion_responsable_doc=self.env.user.partner_id.nit
            if not f.reversion_solicita:
                f.reversion_solicita=f.partner_id.name
            if not f.reversion_solicita_doc:
                if f.partner_id.dui:
                    f.reversion_solicita_tipo_id=self.env.ref('sv_fe.svfe_doc_identificacion_2').id
                    f.reversion_solicita_doc=f.partner_id.dui
                elif f.partner_id.nit:
                    f.reversion_solicita_tipo_id=self.env.ref('sv_fe.svfe_doc_identificacion_1').id
                    f.reversion_solicita_doc=f.partner_id.nit


        dic['tipoAnulacion']=2
        dic['motivoAnulacion']=f.reversion_motivo
        dic['nombreResponsable']=f.reversion_responsable 
        dic['tipDocResponsable']=f.reversion_responsable_tipo_id.codigo 
        dic['numDocResponsable']=f.reversion_responsable_doc.replace('-','') if f.reversion_responsable_doc != False else None 
        dic['nombreSolicita']=f.reversion_solicita
        dic['tipDocSolicita']=f.reversion_solicita_tipo_id.codigo
        dic['numDocSolicita']=f.reversion_solicita_doc.replace('-','') if f.reversion_solicita_doc != False else None
        return dic

    def get_resumen_reve(self):
        self.ensure_one()
        f=self
        resumen={}
        resumen['totalNoSuj']=round(f.nosujetas,2)
        resumen['totalExenta']=round(f.exentas,2)
        resumen['totalGravada']=round(f.gravadas,2)
        resumen['subTotalVentas']=round(f.nosujetas+f.exentas+f.gravadas,2)
        resumen['descuNoSuj']=round(f.nosujetas_des,2)
        resumen['descuExenta']=round(f.exentas_des,2)
        resumen['descuGravada']=round(f.gravadas_des,2)
        resumen['totalDescu']=round(f.nosujetas_des+f.exentas_des+f.gravadas_des,2)
        resumen['porcentajeDescuento']=round((resumen['totalDescu']/resumen['subTotalVentas'])*100,2)
        tributos=[]
        for l in f.invoice_line_ids:
            for t in l.tax_ids:
                if t.fe_tributo_id:
                    if  t.fe_tributo_id.codigo!='20':
                        if not t.fe_tributo_id.codigo in tributos:
                            tributos.append(t.fe_tributo_id.codigo)

        resumen['tributos']=tributos
        resumen['subTotal']=round(resumen['subTotalVentas']-resumen['totalDescu'],2)

        resumen['ivaRete1']=round(f.retencion,2)
        resumen['reteRenta']=round(f.isr,2)
        resumen['montoTotalOperacion']=round(resumen['subTotal'],2)
        resumen['totalNoGravado']=0
        resumen['totalPagar']=round(resumen['montoTotalOperacion']-resumen['ivaRete1']-resumen['reteRenta'],2)
        resumen['totalLetras']=numero_to_letras(round(resumen['totalPagar'],2))
        resumen['totalIva']=round(f.iva,2)
        resumen['saldoFavor']=0
        if f.invoice_payment_term_id.fe_condicion_id:
            resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        else:
            resumen['condicionOperacion']=2
        resumen['pagos']=f.get_pagos()
        resumen['numPagoElectronico']=None
        return resumen        








##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   FACTURA
##-----------------------------------------------------------------------------------------------------------------------------------------------------------
    def get_factura(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_fac()
        dic['documentoRelacionado']=None
        dic['emisor']=f.get_emisor()
        dic['receptor']=f.get_receptor_fact()
        dic['otrosDocumentos']=f.get_otros()
        dic['ventaTercero']=f.get_terceros()
        dic['cuerpoDocumento']=f.get_cuerpo_fac()
        dic['resumen']=f.get_resumen_fac()
        dic['extension']=f.get_extension()
        dic['apendice']=None
        return dic

    def get_identificacion_fac(self):        
        self.ensure_one()
        f=self
        if not f.uuid and not f.proforma:
            f.uuid=str(uuid.uuid4()).upper()
            if f.tipo_documento_id.sequencia_id:
                f.control=f.tipo_documento_id.sequencia_id.next_by_id()
            else:
                f.control=f.tipo_documento_id.fe_tipo_doc_id.sequencia_id.next_by_id()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        identificacion['numeroControl']=f.control
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        identificacion['tipoContingencia']=None if not f.contingencia else int(f.contingencia.fe_contingencia_id.codigo)
        identificacion['motivoContin']=None if not f.contingencia else int(f.contingencia.motivo)
        if not f.proforma:
            identificacion['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%H:%M:%S')
        else:
            identificacion['fecEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'        
        return identificacion

    def get_receptor_fact(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            if f.partner_id.nrc and f.partner_id.nrc=='NA':
                receptor['tipoDocumento']='37'
                receptor['numDocumento']=f.partner_id.nit.replace('-','')
                receptor['nrc']=None
            else:
                if f.partner_id.nit:
                    receptor['tipoDocumento']='36'
                    receptor['numDocumento']=f.partner_id.nit.replace('-','')
                    receptor['nrc']=None
                elif f.partner_id.dui:
                    receptor['tipoDocumento']='13'
                    receptor['numDocumento']=f.partner_id.dui.replace('-','')
                    if f.partner_id.nrc:
                        receptor['nrc']=f.partner_id.nrc
                else:
                    receptor['tipoDocumento']=None
                    receptor['numDocumento']=None
                    receptor['nrc']=None
            
                
            receptor['nombre']=f.partner_id.name
            if f.partner_id.fe_actividad_id:
                receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
                receptor['descActividad']=f.partner_id.fe_actividad_id.name
            else:
                receptor['codActividad']=None
                receptor['descActividad']=None
            receptor['direccion']=f.get_direccion_fact(f.partner_id)
            if f.partner_id.phone:
                receptor['telefono']=f.partner_id.phone
            if f.partner_id.email:
                receptor['correo']=f.partner_id.email
            else:
                receptor['correo']=None
            return receptor
        else:
            return None
    
    def get_direccion_fact(self,partner):
        self.ensure_one()
        f=self
        direccion={}
        if partner.state_id:
            direccion['departamento']=partner.fe_municipio_id.departamento_id.code
        else:
           return None
        if partner.fe_municipio_id:
            direccion['municipio']=partner.fe_municipio_id.codigo
        else:
            return None
        if partner.street:
            direccion['complemento']=partner.street
        else:
            return None
        return direccion

    def get_cuerpo_fac(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=f.extra_discount
        f.exentas_des=0
        f.nosujetas_des=0
        f.gravadas_linea_des=0
        f.exentas_linea_des=0
        f.nosujetas_linea_des=0
        f.retencion=0
        f.percepcion=0
        f.isr=0
        f.iva=0
        f.iva_des=0
        lista=[]
        i=1
        incluido=False
        descuento_global=0.0
        for l in f.invoice_line_ids:
            if l.price_total>0:
                dic={}
                dic['numItem']=i
                if l.product_id and l.product_id.fe_tipo_item_id:
                    dic['tipoItem']=int(l.product_id.fe_tipo_item_id.codigo)
                else:
                    dic['tipoItem']=1
                dic['numeroDocumento']=None
                dic['cantidad']=l.quantity
                dic['codigo']=l.product_id.default_code
                dic['codTributo']=None
                if l.product_uom_id.fe_unidad_id:
                    dic['uniMedida']=int(l.product_uom_id.fe_unidad_id.codigo)
                else:
                    dic['uniMedida']=59
                dic['descripcion']=l.name
                dic['precioUni']=round(l.price_unit,2)
                
                descuento=l.discount/100
                valor_con_descuento=1-descuento
                
                dic['montoDescu']=0
                iva=False
                ivap=0
                ivaitem=0
                price_unit_notax=0
                exento=True
                nosujeto=False
                retencion=False
                persepcion=False
                isr=False
                tributos=[]
                price_unit=l.price_unit
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                    if iva==True:
                        incluido=t.price_include
                        price_unit=price_unit/(1+ivap)
                    if incluido:
                        price_unit=l.price_unit
                        price_unit_notax=l.price_unit/(1+ivap)
                        ivaitem=(l.price_unit*valor_con_descuento)-((l.price_unit*valor_con_descuento)/(1+ivap))
                        #raise UserError(str(ivaitem)+" price_unit:"+str(l.price_unit)+" valor descuento:"+str(valor_con_descuento)+"  ivap:"+str(ivap))
                    else:
                        price_unit=l.price_unit*(1+ivap)
                        price_unit_notax=l.price_unit
                        ivaitem=(l.price_unit*valor_con_descuento)*ivap
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                    retencion=True if t.tax_group_id.code=='retencion' else False
                    persepcion=True if t.tax_group_id.code=='persepcion' else False
                    isr=True if t.tax_group_id.code=='isr' else False

                    f.retencion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='retencion' else 0
                    f.percepcion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='persepcion' else 0
                    f.isr+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='isr' else 0
                    if t.fe_tributo_id:
                        if  t.fe_tributo_id.codigo!='20':
                            tributos.append(t.fe_tributo_id.codigo)
                dic['precioUni']=round(price_unit,6)
                if iva or retencion or persepcion:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=0
                    dic['ventaGravada']=round((price_unit*l.quantity*valor_con_descuento),6)                    
                    dic['montoDescu']= round(price_unit*l.quantity*descuento,6)
                    f.gravadas_linea_des+=dic['montoDescu']
                elif exento:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=round((price_unit*l.quantity*valor_con_descuento),6)
                    dic['ventaGravada']=0
                    dic['montoDescu']=  round(price_unit*l.quantity*descuento,6)
                    f.exentas_linea_des+=dic['montoDescu']
                elif nosujeto:
                    dic['ventaNoSuj']=round((price_unit*l.quantity*valor_con_descuento),6)
                    dic['ventaExenta']=0
                    dic['ventaGravada']=0
                    dic['montoDescu']=  round(price_unit*l.quantity*descuento,6)
                    f.nosujetas_linea_des+=dic['montoDescu']
                else:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=0
                    dic['ventaGravada']=0
                f.gravadas+=dic['ventaGravada']
                f.exentas+=dic['ventaExenta']
                f.nosujetas+=dic['ventaNoSuj']
                if len(tributos)>0:
                    dic['tributos']=tributos
                else:
                    dic['tributos']=None
                dic['psv']=0
                dic['noGravado']=0                
                dic['ivaItem']=round(ivaitem*l.quantity,6)
                f.iva+=dic['ivaItem']
                #f.iva+=round(ivaitem*l.quantity,2)
                lista.append(dic)
                i+=1
            else:
                descuento_global+=(l.price_total*-1)
                iva=False
                exento=True
                nosujeto=False
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                if iva or retencion or persepcion:
                    f.gravadas_des+=(l.price_total*-1)
                elif exento:
                    f.exentas_des+=(l.price_total*-1)
                elif nosujeto:
                    f.nosujetas_des+=(l.price_total*-1)
                iva=False
                ivap=0
                exento=True
                nosujeto=False
                retencion=False
                persepcion=False
                isr=False
                tributos=[]
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                f.iva+=(round((l.price_unit*l.quantity)*(ivap),6))
                f.iva_des+=(round((l.price_unit*l.quantity*-1)*(ivap),6))            
        return lista

    def get_resumen_fac(self):
        self.ensure_one()
        f=self
        resumen={}
        resumen['totalNoSuj']=round(f.nosujetas,2)
        resumen['totalExenta']=round(f.exentas,2)
        resumen['totalGravada']=round(f.gravadas,2)
        resumen['subTotalVentas']=round(f.nosujetas+f.exentas+f.gravadas,2)
        resumen['descuNoSuj']=round(f.nosujetas_des,2)
        resumen['descuExenta']=round(f.exentas_des,2)
        resumen['descuGravada']=round(f.gravadas_des,2)
        resumen['totalDescu']=round(f.nosujetas_des+f.exentas_des+f.gravadas_des+f.exentas_linea_des+f.nosujetas_linea_des+f.gravadas_linea_des,2)
        resumen['porcentajeDescuento']=round((resumen['totalDescu']/resumen['subTotalVentas'])*100,2)
        tributos=[]
        for l in f.invoice_line_ids:
            for t in l.tax_ids:
                if t.fe_tributo_id:
                    if  t.fe_tributo_id.codigo!='20':
                        if not t.fe_tributo_id.codigo in tributos:
                            tributos.append(t.fe_tributo_id.codigo)

        resumen['tributos']=tributos
        resumen['subTotal']=round(resumen['subTotalVentas']-resumen['descuNoSuj']-resumen['descuExenta']-resumen['descuGravada'],2)
        #resumen['subTotal']=round(resumen['subTotalVentas'],2)
        resumen['ivaRete1']=round(f.retencion*-1,2)
        resumen['reteRenta']=round(f.isr*-1,2)
        resumen['montoTotalOperacion']=round(resumen['subTotal'],2)
        resumen['totalNoGravado']=0
        resumen['totalPagar']=round(resumen['montoTotalOperacion']-resumen['ivaRete1']-resumen['reteRenta'],2)
        resumen['totalLetras']=numero_to_letras(round(resumen['totalPagar'],2))
        resumen['totalIva']=round(f.iva,2)
        resumen['saldoFavor']=0
        if f.invoice_payment_term_id.fe_condicion_id:
            resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        else:
            resumen['condicionOperacion']=2
        resumen['pagos']=f.get_pagos()
        resumen['numPagoElectronico']=None
        return resumen        

##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   CCF
##-----------------------------------------------------------------------------------------------------------------------------------------------------------
    def get_ccf(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_ccf()
        dic['documentoRelacionado']=None
        dic['emisor']=f.get_emisor()
        dic['receptor']=f.get_receptor_ccf()
        dic['otrosDocumentos']=f.get_otros()
        dic['ventaTercero']=f.get_terceros()
        dic['cuerpoDocumento']=f.get_cuerpo_ccf()
        dic['resumen']=f.get_resumen_ccf()
        dic['extension']=f.get_extension()
        dic['apendice']=None
        return dic
    
    def get_identificacion_ccf(self):        
        self.ensure_one()
        f=self
        if not f.uuid and not f.proforma:
            f.uuid=str(uuid.uuid4()).upper()
            if f.tipo_documento_id.sequencia_id:
                f.control=f.tipo_documento_id.sequencia_id.next_by_id()
            else:
                f.control=f.tipo_documento_id.fe_tipo_doc_id.sequencia_id.next_by_id()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        identificacion['numeroControl']=f.control
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        identificacion['tipoContingencia']=None if not f.contingencia else int(f.contingencia.fe_contingencia_id.codigo)
        identificacion['motivoContin']=None if not f.contingencia else int(f.contingencia.motivo)
        if not f.proforma:
            identificacion['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%H:%M:%S')
        else:
            identificacion['fecEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'        
        return identificacion

    def get_receptor_ccf(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            receptor['nit']=f.partner_id.nit.replace('-','')
            receptor['nrc']=f.partner_id.nrc.replace('-','')
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            receptor['nombreComercial']=f.partner_id.name
            receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['correo']=f.partner_id.email
            return receptor
        else:
            return None

    def get_cuerpo_ccf(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=f.extra_discount
        f.exentas_des=0
        f.nosujetas_des=0
        f.gravadas_linea_des=0
        f.exentas_linea_des=0
        f.nosujetas_linea_des=0

        f.retencion=0
        f.percepcion=0
        f.isr=0
        f.iva=0
        f.iva_des=0
        lista=[]
        i=1
        descuento_global=0
        for l in f.invoice_line_ids:
            if l.price_total>0:
                dic={}
                dic['numItem']=i
                if l.product_id and l.product_id.fe_tipo_item_id:
                    dic['tipoItem']=int(l.product_id.fe_tipo_item_id.codigo)
                else:
                    dic['tipoItem']=1
                dic['numeroDocumento']=None
                dic['cantidad']=l.quantity
                dic['codigo']=l.product_id.default_code
                dic['codTributo']=None
                if l.product_uom_id.fe_unidad_id:
                    dic['uniMedida']=int(l.product_uom_id.fe_unidad_id.codigo)
                else:
                    dic['uniMedida']=59
                dic['descripcion']=l.name
                

                descuento=l.discount/100
                valor_con_descuento=1-descuento
                
                dic['montoDescu']=0
                iva=False
                ivap=0
                exento=True
                nosujeto=False
                retencion=False
                persepcion=False
                isr=False
                tributos=[]
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                    if iva==True:
                        incluido=t.price_include
                        price_unit=l.price_unit/(1+ivap)
                    if incluido:
                        price_unit=l.price_unit
                        price_unit_notax=l.price_unit/(1+ivap)
                        ivaitem=(l.price_unit*valor_con_descuento)-(l.price_unit/(1+ivap))
                    else:
                        price_unit=l.price_unit*(1+ivap)
                        price_unit_notax=l.price_unit
                        ivaitem=(l.price_unit*valor_con_descuento)*ivap
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                    retencion=True if t.tax_group_id.code=='retencion' else False
                    persepcion=True if t.tax_group_id.code=='persepcion' else False
                    isr=True if t.tax_group_id.code=='isr' else False

                    f.retencion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='retencion' else 0
                    f.percepcion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='persepcion' else 0
                    f.isr+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='isr' else 0
                    if t.fe_tributo_id:
                        tributos.append(t.fe_tributo_id.codigo)
                dic['precioUni']=round(price_unit_notax,6)
                if iva or retencion or persepcion:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=0
                    dic['ventaGravada']=round((price_unit_notax*l.quantity*valor_con_descuento),6)
                    dic['montoDescu']= round(price_unit_notax*l.quantity*descuento,6)
                    f.gravadas_linea_des+=dic['montoDescu']
                elif exento:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=round((price_unit_notax*l.quantity*valor_con_descuento),6)
                    dic['ventaGravada']=0
                    dic['montoDescu']= round(price_unit_notax*l.quantity*descuento,6)
                    f.exentas_linea_des+=dic['montoDescu']
                elif nosujeto:
                    dic['ventaNoSuj']=round((price_unit_notax*l.quantity*valor_con_descuento),6)
                    dic['ventaExenta']=0
                    dic['ventaGravada']=0
                    dic['montoDescu']= round(price_unit_notax*l.quantity*descuento,6)
                    f.nosujetas_linea_des+=dic['montoDescu']
                else:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=0
                    dic['ventaGravada']=0
                f.gravadas+=dic['ventaGravada']
                f.exentas+=dic['ventaExenta']
                f.nosujetas+=dic['ventaNoSuj']
                if len(tributos)>0:
                    dic['tributos']=tributos
                else:
                    dic['tributos']=None
                dic['psv']=0
                dic['noGravado']=0
                f.iva+=(round((price_unit_notax*l.quantity*valor_con_descuento)*(ivap),6))
                lista.append(dic)
                i+=1
            else:
                descuento_global+=(l.price_total*-1)
                iva=False
                exento=True
                nosujeto=False
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                if iva or retencion or persepcion:
                    f.gravadas_des+=(l.price_subtotal*-1)
                elif exento:
                    f.exentas_des+=(l.price_subtotal*-1)
                elif nosujeto:
                    f.nosujetas_des+=(l.price_subtotal*-1)
                iva=False
                ivap=0
                exento=True
                nosujeto=False
                retencion=False
                persepcion=False
                isr=False
                tributos=[]
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                    if iva==True:
                        incluido=t.price_include
                        price_unit=price_unit/(1+ivap)
                    if incluido:
                        price_unit=l.price_unit
                        price_unit_notax=l.price_unit/(1+ivap)
                    else:
                        price_unit=l.price_unit*(1+ivap)
                        price_unit_notax=l.price_unit
                f.iva+=(round((price_unit_notax*l.quantity)*(ivap),6))
                f.iva_des+=(round((price_unit_notax*l.quantity*-1)*(ivap),6))
            
        return lista

    def get_resumen_ccf(self):
        self.ensure_one()
        f=self
        resumen={}
        resumen['totalNoSuj']=round(f.nosujetas,2)
        resumen['totalExenta']=round(f.exentas,2)
        resumen['totalGravada']=round(f.gravadas,2)
        resumen['subTotalVentas']=round(f.nosujetas+f.exentas+f.gravadas,2)
        total=resumen['subTotalVentas']+f.iva
        resumen['descuNoSuj']=round(f.nosujetas_des,2)
        resumen['descuExenta']=round(f.exentas_des,2)
        resumen['descuGravada']=round(f.gravadas_des,2)
        resumen['totalDescu']=round(f.nosujetas_des+f.exentas_des+f.gravadas_des+f.exentas_linea_des+f.nosujetas_linea_des+f.gravadas_linea_des,2)
        resumen['porcentajeDescuento']=round((resumen['totalDescu']/resumen['subTotalVentas'])*100,2)
        tributos=[]
        for l in f.invoice_line_ids:
            if l.price_total>0:
                for t in l.tax_ids:
                    if t.fe_tributo_id:
                        if  t.fe_tributo_id.codigo!='0':
                            if not t.id in tributos:                            
                                tributos.append(t.id)
        if len(tributos)>0:
            tributosmh=[]
            for t in tributos:
                tmh={}
                tax=self.env['account.tax'].browse(t)
                tmh['codigo']=tax.fe_tributo_id.codigo
                tmh['descripcion']=tax.fe_tributo_id.name
                valor=0
                for l in f.line_ids:
                   if l.tax_line_id and l.tax_line_id.id==t:
                      valor=l.credit-l.debit if l.credit>l.debit else l.debit-l.credit
                tmh['valor']=round(valor,2)
                tributosmh.append(tmh)
            resumen['tributos']=tributosmh
        else:
            resumen['tributos']=None
        resumen['subTotal']=round(resumen['subTotalVentas']-resumen['descuNoSuj']-resumen['descuExenta']-resumen['descuGravada'],2)
        resumen['ivaPerci1']=round(f.percepcion*-1,2)
        resumen['ivaRete1']=round(f.retencion*-1,2)
        resumen['reteRenta']=round(f.isr,2)
        resumen['montoTotalOperacion']=round(resumen['subTotal']+f.iva,2)
        resumen['totalNoGravado']=0
        resumen['totalPagar']=round(resumen['montoTotalOperacion']-resumen['ivaRete1']-resumen['reteRenta'],2)
        resumen['totalLetras']=numero_to_letras(round(resumen['totalPagar'],2))
        resumen['saldoFavor']=0
        if f.invoice_payment_term_id.fe_condicion_id:
            resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        else:
            resumen['condicionOperacion']=2
        resumen['pagos']=f.get_pagos()
        resumen['numPagoElectronico']=None
        return resumen



##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   COMPROBANDE DE RETENCION
##-----------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def get_cr(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_cr()
        dic['emisor']=f.get_emisor_cr()
        dic['receptor']=f.get_receptor_cr()

        dic['cuerpoDocumento']=f.get_cuerpo_cr()
        dic['resumen']=f.get_resumen_cr()
        dic['extension']=f.get_extension()
        dic['apendice']=None
        return dic

    def get_emisor_cr(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nrc']=f.company_id.partner_id.nrc.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['codActividad']=f.company_id.partner_id.fe_actividad_id.codigo
        emisor['descActividad']=f.company_id.partner_id.fe_actividad_id.name
        emisor['nombreComercial']=None
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['direccion']=f.get_direccion(f.company_id.partner_id)
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codigo']=None
        emisor['codigoMH']=None
        emisor['puntoVentaMH']=None
        emisor['puntoVenta']=None
        return emisor
    
    def get_relacionado_cr(self):
        self.ensure_one()
        f=self
        if f.doc_relacionado:
            docs=[]
            doc={}
            doc['tipoDocumento']=f.doc_relacionado.tipo_documento_id.fe_tipo_doc_id.codigo
            doc['tipoGeneracion']=2 if f.doc_relacionado.uuid else 1
            doc['numeroDocumento']=f.doc_relacionado.uuid if f.doc_relacionado.uuid else f.doc_relacionado.doc_numero
            doc['fechaEmision']=f.doc_relacionado.invoice_date.strftime('%Y-%m-%d')
            docs.append(doc)
            return docs
        else:
            return None
       

    def get_identificacion_cr(self):        
        self.ensure_one()
        f=self
        if not f.uuid and not f.proforma:
            f.uuid=str(uuid.uuid4()).upper()
            if f.tipo_documento_id.sequencia_id:
                f.control=f.tipo_documento_id.sequencia_id.next_by_id()
            else:
                f.control=f.tipo_documento_id.fe_tipo_doc_id.sequencia_id.next_by_id()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        identificacion['numeroControl']=f.control
        #f.control=identificacion['numeroControl']
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        identificacion['tipoContingencia']=None if not f.contingencia else int(f.contingencia.fe_contingencia_id.codigo)
        identificacion['motivoContin']=None if not f.contingencia else int(f.contingencia.motivo)
        if not f.proforma:
            identificacion['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%H:%M:%S')
        else:
            identificacion['fecEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'        
        return identificacion

    def get_receptor_cr(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            if f.partner_id.nit:
                receptor['tipoDocumento']='36'
                receptor['numDocumento']=f.partner_id.nit.replace('-','')
            else:
                receptor['tipoDocumento']='37'
                receptor['numDocumento']=f.partner_id.nrc.replace('-','')
            #receptor['nit']=f.partner_id.nit.replace('-','')
            receptor['nrc']=f.partner_id.nrc.replace('-','')
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            receptor['nombreComercial']=f.partner_id.comercial
            #receptor['tipoEstablecimiento']=f.fe_establecimiento_id.codigo
            receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['correo']=f.partner_id.email
            #receptor['codEstableMH']=None
            #receptor['codEstable']=None
            #receptor['codPuntoVentaMH']=None
            #receptor['codPuntoVenta']=None
            return receptor
        else:
            return None

    def get_cuerpo_cr(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=f.extra_discount
        f.exentas_des=0
        f.nosujetas_des=0
        f.retencion=0
        f.percepcion=0
        f.isr=0
        f.iva=0
        lista=[]
        dic={}
        i=1
        for l in f.invoice_line_ids:            
            iva=False
            ivap=0
            exento=True
            nosujeto=False
            retencion=False
            persepcion=False
            isr=False

            descuento=l.discount/100
            valor_con_descuento=1-descuento
            
            tributos=[]
            for t in l.tax_ids:
                iva=True if t.tax_group_id.code=='iva' else False
                ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                exento=True if t.tax_group_id.code=='exento' else False
                nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                retencion=True if t.tax_group_id.code=='retencion' else False
                persepcion=True if t.tax_group_id.code=='persepcion' else False
                isr=True if t.tax_group_id.code=='isr' else False

                f.retencion+=((l.price_unit*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='retencion' else 0
                f.percepcion+=((l.price_unit*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='persepcion' else 0
                f.isr+=((l.price_unit*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='isr' else 0
                if t.fe_tributo_id:
                    tributos.append(t.fe_tributo_id.codigo)            
            #dic['compra']=l.price_subtotal
            f.nosujetas+=l.price_subtotal
            if iva or retencion or persepcion:
                f.gravadas+=round((l.price_unit*l.quantity*valor_con_descuento),2)
                f.gravadas_des+=(l.price_unit*l.quantity*descuento)
            elif exento:
                f.exentas+=round((l.price_unit*l.quantity*valor_con_descuento),2)
                f.exentas_des+=(l.price_unit*l.quantity*descuento)
            elif nosujeto:
                f.nosujetas+=round((l.price_unit*l.quantity*valor_con_descuento),2)
                f.nosujetas_des+=(l.price_unit*l.quantity*descuento)    
            i+=1
        if len(f.doc_numero)>30:
            dic['numItem']=1
            dic['tipoDte']='03'
            dic['tipoDoc']=2
            dic['numDocumento']=f.doc_numero
            dic['fechaEmision']=f.invoice_date.strftime('%Y-%m-%d')
            dic['montoSujetoGrav']=round(f.gravadas,2)
            dic['codigoRetencionMH']='22'
            dic['ivaRetenido']=round(f.retencion,2)
            dic['descripcion']=f.observaciones
            ##dic['descripcion']=
        else:
            dic['numItem']=1
            dic['tipoDoc']=1
            dic['tipoDte']='03'
            dic['numDocumento']=f.doc_numero
            dic['fechaEmision']=f.invoice_date.strftime('%Y-%m-%d')
            dic['montoSujetoGrav']=round(f.gravadas,2)
            dic['codigoRetencionMH']='22'
            dic['ivaRetenido']=round(f.retencion*1,2)
            dic['descripcion']=f.observaciones
        lista.append(dic)
        return lista

    def get_resumen_cr(self):
        self.ensure_one()
        f=self
        resumen={}

        resumen['totalSujetoRetencion']=round(f.gravadas,2)
        resumen['totalIVAretenido']=round(f.retencion*1,2)
        resumen['totalIVAretenidoLetras']=numero_to_letras(round(f.retencion,2))

        return resumen








##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   NOTA CREDITO
##-----------------------------------------------------------------------------------------------------------------------------------------------------------        
    def get_nc(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_nc()
        dic['documentoRelacionado']=f.get_relacionado_nc()
        dic['emisor']=f.get_emisor_nc()
        dic['receptor']=f.get_receptor_nc()
        #dic['otrosDocumentos']=f.get_otros()
        dic['ventaTercero']=f.get_terceros()
        dic['cuerpoDocumento']=f.get_cuerpo_nc()
        dic['resumen']=f.get_resumen_nc()
        dic['extension']=f.get_extension()
        dic['apendice']=None
        return dic

    def get_emisor_nc(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nrc']=f.company_id.partner_id.nrc.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['codActividad']=f.company_id.partner_id.fe_actividad_id.codigo
        emisor['descActividad']=f.company_id.partner_id.fe_actividad_id.name
        emisor['nombreComercial']=None
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['direccion']=f.get_direccion(f.company_id.partner_id)
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email

        return emisor
    
    def get_relacionado_nc(self):
        self.ensure_one()
        f=self
        if f.doc_relacionado:
            docs=[]
            doc={}
            doc['tipoDocumento']=f.doc_relacionado.tipo_documento_id.fe_tipo_doc_id.codigo
            doc['tipoGeneracion']=2 if f.doc_relacionado.uuid else 1
            doc['numeroDocumento']=f.doc_relacionado.uuid if f.doc_relacionado.uuid else f.doc_relacionado.doc_numero
            doc['fechaEmision']=f.doc_relacionado.invoice_date.strftime('%Y-%m-%d')
            docs.append(doc)
            return docs
        else:
            return None

    def get_identificacion_nc(self):        
        self.ensure_one()
        f=self
        if not f.uuid and not f.proforma:
            f.uuid=str(uuid.uuid4()).upper()
            if f.tipo_documento_id.sequencia_id:
                f.control=f.tipo_documento_id.sequencia_id.next_by_id()
            else:
                f.control=f.tipo_documento_id.fe_tipo_doc_id.sequencia_id.next_by_id()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        #identificacion['numeroControl']='DTE-'+f.tipo_documento_id.fe_tipo_doc_id.codigo.zfill(2)+'-00000000-'+str(f.id).rjust(15,'0')
        identificacion['numeroControl']=f.control
        #f.control=identificacion['numeroControl']
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        identificacion['tipoContingencia']=None if not f.contingencia else int(f.contingencia.fe_contingencia_id.codigo)
        identificacion['motivoContin']=None if not f.contingencia else int(f.contingencia.motivo)
        if not f.proforma:
            identificacion['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%H:%M:%S')
        else:
            identificacion['fecEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'        
        return identificacion

    def get_receptor_nc(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            receptor['nit']=f.partner_id.nit.replace('-','') if f.partner_id.nit else None
            receptor['nrc']=f.partner_id.nrc.replace('-','') if f.partner_id.nrc else None
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            
            receptor['nombreComercial']=f.partner_id.comercial if f.partner_id.comercial else f.partner_id.name
            #receptor['tipoEstablecimiento']=f.fe_establecimiento_id.codigo
            receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['correo']=f.partner_id.email
            #receptor['codEstableMH']=None
            #receptor['codEstable']=None
            #receptor['codPuntoVentaMH']=None
            #receptor['codPuntoVenta']=None
            return receptor
        else:
            return None

    def get_cuerpo_nc(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=f.extra_discount
        f.exentas_des=0
        f.nosujetas_des=0
        f.gravadas_linea_des=0
        f.exentas_linea_des=0
        f.nosujetas_linea_des=0
        f.retencion=0
        f.percepcion=0
        f.isr=0
        f.iva=0
        lista=[]
        i=1
        descuento_global=0
        for l in f.invoice_line_ids:
            if l.price_total>0:
                dic={}
                dic['numItem']=i
                if l.product_id and l.product_id.fe_tipo_item_id:
                    dic['tipoItem']=int(l.product_id.fe_tipo_item_id.codigo)
                else:
                    dic['tipoItem']=1
                dic['numeroDocumento']=f.doc_relacionado.uuid if f.doc_relacionado.uuid else f.doc_relacionado.doc_numero
                dic['cantidad']=l.quantity
                dic['codigo']=l.product_id.default_code
                dic['codTributo']=None
                if l.product_uom_id.fe_unidad_id:
                    dic['uniMedida']=int(l.product_uom_id.fe_unidad_id.codigo)
                else:
                    dic['uniMedida']=59
                dic['descripcion']=l.name
                dic['precioUni']=l.price_unit

                descuento=l.discount/100
                valor_con_descuento=1-descuento

                dic['montoDescu']=(l.price_unit*l.quantity*descuento)
                iva=False
                ivap=0
                exento=True
                nosujeto=False
                retencion=False
                persepcion=False
                isr=False
                tributos=[]
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                    if iva==True:
                        incluido=t.price_include
                        price_unit=l.price_unit/(1+ivap)
                    if incluido:
                        price_unit=l.price_unit
                        price_unit_notax=l.price_unit/(1+ivap)
                        ivaitem=(l.price_unit*valor_con_descuento)-(l.price_unit/(1+ivap))
                    else:
                        price_unit=l.price_unit*(1+ivap)
                        price_unit_notax=l.price_unit
                        ivaitem=(l.price_unit*valor_con_descuento)*ivap
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                    retencion=True if t.tax_group_id.code=='retencion' else False
                    persepcion=True if t.tax_group_id.code=='persepcion' else False
                    isr=True if t.tax_group_id.code=='isr' else False

                    f.retencion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='retencion' else 0
                    f.percepcion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='persepcion' else 0
                    f.isr+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='isr' else 0
                    if t.fe_tributo_id:
                        tributos.append(t.fe_tributo_id.codigo)
                dic['precioUni']=round(price_unit_notax,6)
                if iva or retencion or persepcion:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=0
                    dic['ventaGravada']=round((price_unit_notax*l.quantity*valor_con_descuento),6)
                    dic['montoDescu']= round(price_unit_notax*l.quantity*descuento,6)
                    f.gravadas_linea_des+=dic['montoDescu']
                elif exento:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=round((price_unit_notax*l.quantity*valor_con_descuento),6)
                    dic['ventaGravada']=0
                    dic['montoDescu']= round(price_unit_notax*l.quantity*descuento,6)
                    f.exentas_linea_des+=dic['montoDescu']
                elif nosujeto:
                    dic['ventaNoSuj']=round((price_unit_notax*l.quantity*valor_con_descuento),6)
                    dic['ventaExenta']=0
                    dic['ventaGravada']=0
                    dic['montoDescu']= round(price_unit_notax*l.quantity*descuento,6)
                    f.nosujetas_linea_des+=dic['montoDescu']
                else:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=0
                    dic['ventaGravada']=0
                f.gravadas+=dic['ventaGravada']
                f.exentas+=dic['ventaExenta']
                f.nosujetas+=dic['ventaNoSuj']
                if len(tributos)>0:
                    dic['tributos']=tributos
                else:
                    dic['tributos']=None
                f.iva+=(round((price_unit_notax*l.quantity*valor_con_descuento)*(ivap),6))
                lista.append(dic)
                i+=1
            else:
                descuento_global+=(l.price_total*-1)
                iva=False
                exento=True
                nosujeto=False
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                if iva or retencion or persepcion:
                    f.gravadas_des+=(l.price_subtotal*-1)
                elif exento:
                    f.exentas_des+=(l.price_subtotal*-1)
                elif nosujeto:
                    f.nosujetas_des+=(l.price_subtotal*-1)
                iva=False
                ivap=0
                exento=True
                nosujeto=False
                retencion=False
                persepcion=False
                isr=False
                tributos=[]
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                    if iva==True:
                        incluido=t.price_include
                        price_unit=price_unit/(1+ivap)
                    if incluido:
                        price_unit=l.price_unit
                        price_unit_notax=l.price_unit/(1+ivap)
                    else:
                        price_unit=l.price_unit*(1+ivap)
                        price_unit_notax=l.price_unit
                f.iva+=(round((price_unit_notax*l.quantity)*(ivap),6))
                f.iva_des+=(round((price_unit_notax*l.quantity*-1)*(ivap),6))
            
        return lista

    def get_resumen_nc(self):
        self.ensure_one()
        f=self
        resumen={}
        resumen['totalNoSuj']=round(f.nosujetas,2)
        resumen['totalExenta']=round(f.exentas,2)
        resumen['totalGravada']=round(f.gravadas,2)
        resumen['subTotalVentas']=round(f.nosujetas+f.exentas+f.gravadas,2)
        total=resumen['subTotalVentas']+f.iva
        resumen['descuNoSuj']=round(f.nosujetas_des,2)
        resumen['descuExenta']=round(f.exentas_des,2)
        resumen['descuGravada']=round(f.gravadas_des,2)
        resumen['totalDescu']=round(f.nosujetas_des+f.exentas_des+f.gravadas_des+f.exentas_linea_des+f.nosujetas_linea_des+f.gravadas_linea_des,2)
        #resumen['porcentajeDescuento']=round((resumen['totalDescu']/resumen['subTotalVentas'])*100,2)
        tributos=[]
        for l in f.invoice_line_ids:
            for t in l.tax_ids:
                if t.fe_tributo_id:
                    if  t.fe_tributo_id.codigo!='0':
                        if not t.id in tributos:                            
                            tributos.append(t.id)
        if len(tributos)>0:
            tributosmh=[]
            for t in tributos:
                tmh={}
                tax=self.env['account.tax'].browse(t)
                tmh['codigo']=tax.fe_tributo_id.codigo
                tmh['descripcion']=tax.fe_tributo_id.name
                valor=0
                for l in f.line_ids:
                   if l.tax_line_id and l.tax_line_id.id==t:
                      valor=l.credit-l.debit if l.credit>l.debit else l.debit-l.credit
                tmh['valor']=valor
                tributosmh.append(tmh)
            resumen['tributos']=tributosmh
        else:
            resumen['tributos']=None
        resumen['subTotal']=round(resumen['subTotalVentas']-resumen['descuNoSuj']-resumen['descuExenta']-resumen['descuGravada'],2)
        resumen['ivaPerci1']=round(f.percepcion*-1,2)
        resumen['ivaRete1']=round(f.retencion*-1,2)
        resumen['reteRenta']=round(f.isr,2)
        resumen['montoTotalOperacion']=round(resumen['subTotal']+f.iva,2)
        #resumen['totalNoGravado']=0
        #resumen['totalPagar']=round(resumen['montoTotalOperacion'],2)
        resumen['totalLetras']=numero_to_letras(round(resumen['montoTotalOperacion'],2))
        ##resumen['totalIva']=round(f.iva,2)
        #resumen['saldoFavor']=0
        if f.invoice_payment_term_id.fe_condicion_id:
            resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        else:
            resumen['condicionOperacion']=2
        return resumen


##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   SUJETO EXCLUIDO
##-----------------------------------------------------------------------------------------------------------------------------------------------------------        
    def get_se(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_se()
        #dic['documentoRelacionado']=f.get_relacionado_se()
        dic['emisor']=f.get_emisor_se()
        dic['sujetoExcluido']=f.get_receptor_se()
        #dic['otrosDocumentos']=f.get_otros()
        #dic['ventaTercero']=f.get_terceros()
        dic['cuerpoDocumento']=f.get_cuerpo_se()
        dic['resumen']=f.get_resumen_se()
        #dic['extension']=f.get_extension()
        dic['apendice']=None
        return dic

    def get_emisor_se(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nrc']=f.company_id.partner_id.nrc.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['codActividad']=f.company_id.partner_id.fe_actividad_id.codigo
        emisor['descActividad']=f.company_id.partner_id.fe_actividad_id.name
        #emisor['nombreComercial']=None
        #emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['direccion']=f.get_direccion(f.company_id.partner_id)
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codEstableMH']=None
        emisor['codEstable']=None
        emisor['codPuntoVentaMH']=None
        emisor['codPuntoVenta']=None
        return emisor
    
    def get_relacionado_se(self):
        self.ensure_one()
        f=self
        if f.doc_relacionado:
            docs=[]
            doc={}
            doc['tipoDocumento']=f.doc_relacionado.tipo_documento_id.fe_tipo_doc_id.codigo
            doc['tipoGeneracion']=2 if f.doc_relacionado.uuid else 1
            doc['numeroDocumento']=f.doc_relacionado.uuid if f.doc_relacionado.uuid else f.doc_relacionado.doc_numero
            doc['fechaEmision']=f.doc_relacionado.invoice_date.strftime('%Y-%m-%d')
            docs.append(doc)
            return docs
        else:
            return None
       

    def get_identificacion_se(self):        
        self.ensure_one()
        f=self
        if not f.uuid and not f.proforma:
            f.uuid=str(uuid.uuid4()).upper()
            if f.tipo_documento_id.sequencia_id:
                f.control=f.tipo_documento_id.sequencia_id.next_by_id()
            else:
                f.control=f.tipo_documento_id.fe_tipo_doc_id.sequencia_id.next_by_id()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        #identificacion['numeroControl']='DTE-'+f.tipo_documento_id.fe_tipo_doc_id.codigo.zfill(2)+'-00000000-'+str(f.id).rjust(15,'0')
        identificacion['numeroControl']=f.control
        #f.control=identificacion['numeroControl']
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        identificacion['tipoContingencia']=None if not f.contingencia else int(f.contingencia.fe_contingencia_id.codigo)
        identificacion['motivoContin']=None if not f.contingencia else int(f.contingencia.motivo)
        if not f.proforma:
            identificacion['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%H:%M:%S')
        else:
            identificacion['fecEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'        
        return identificacion

    def get_receptor_se(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            if f.partner_id.dui:
                receptor['tipoDocumento']='13'
                receptor['numDocumento']=f.partner_id.dui.replace('-','')
            else:
                receptor['tipoDocumento']='37'
                receptor['numDocumento']=f.partner_id.nit.replace('-','')
            #receptor['nit']=f.partner_id.nit.replace('-','')
            #receptor['nrc']=f.partner_id.nrc.replace('-','')
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            #receptor['nombreComercial']=f.partner_id.comercial
            #receptor['tipoEstablecimiento']=f.fe_establecimiento_id.codigo
            receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['correo']=f.partner_id.email
            #receptor['codEstableMH']=None
            #receptor['codEstable']=None
            #receptor['codPuntoVentaMH']=None
            #receptor['codPuntoVenta']=None
            return receptor
        else:
            return None

    def get_cuerpo_se(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=f.extra_discount
        f.exentas_des=0
        f.nosujetas_des=0
        f.retencion=0
        f.percepcion=0
        f.isr=0
        f.iva=0
        lista=[]
        i=1
        for l in f.invoice_line_ids:
            dic={}
            dic['numItem']=i
            if l.product_id and l.product_id.fe_tipo_item_id:
                dic['tipoItem']=int(l.product_id.fe_tipo_item_id.codigo)
            else:
                dic['tipoItem']=1
            dic['cantidad']=l.quantity
            dic['codigo']=l.product_id.default_code if l.product_id.default_code else 'NA'
            if l.product_uom_id.fe_unidad_id:
                dic['uniMedida']=int(l.product_uom_id.fe_unidad_id.codigo)
            else:
                dic['uniMedida']=59
            dic['descripcion']=l.name
            dic['precioUni']=l.price_unit


            descuento=l.discount/100
            valor_con_descuento=1-descuento
            
            dic['montoDescu']=(l.price_unit*l.quantity*descuento)
            iva=False
            ivap=0
            exento=True
            nosujeto=False
            retencion=False
            persepcion=False
            isr=False
            tributos=[]
            for t in l.tax_ids:
                iva=True if t.tax_group_id.code=='iva' else False
                ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                exento=True if t.tax_group_id.code=='exento' else False
                nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                retencion=True if t.tax_group_id.code=='retencion' else False
                persepcion=True if t.tax_group_id.code=='persepcion' else False
                isr=True if t.tax_group_id.code=='isr' else False

                f.retencion+=((l.price_unit*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='retencion' else 0
                f.percepcion+=((l.price_unit*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='persepcion' else 0
                f.isr+=((l.price_unit*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='isr' else 0
                if t.fe_tributo_id:
                    tributos.append(t.fe_tributo_id.codigo)
            dic['compra']=l.price_subtotal
            f.nosujetas+=l.price_subtotal
            lista.append(dic)
            i+=1
        return lista

    def get_resumen_se(self):
        self.ensure_one()
        f=self
        resumen={}
        #resumen['totalNoSuj']=round(f.nosujetas,2)
        #resumen['totalExenta']=round(f.exentas,2)
        #resumen['totalGravada']=round(f.gravadas,2)
        #resumen['subTotalVentas']=round(f.nosujetas+f.exentas+f.gravadas,2)
        #total=resumen['subTotalVentas']+f.iva
        #resumen['descuNoSuj']=round(f.nosujetas_des,2)
        #resumen['descuExenta']=round(f.exentas_des,2)
        #resumen['descuGravada']=round(f.gravadas_des,2)
        resumen['descu']=0
        resumen['totalDescu']=round(f.nosujetas_des+f.exentas_des+f.gravadas_des,2)
        #resumen['porcentajeDescuento']=round((resumen['totalDescu']/resumen['subTotalVentas'])*100,2)
        
        resumen['subTotal']=round(f.nosujetas,2)
        #resumen['ivaPerci1']=round(f.percepcion,2)
        resumen['ivaRete1']=round(f.retencion,2)
        resumen['reteRenta']=round(abs(f.isr),2)
        #resumen['montoTotalOperacion']=round(resumen['subTotal']-resumen['reteRenta']+f.iva,2)
        resumen['totalCompra']=round(f.nosujetas,2)
        resumen['totalPagar']=round(resumen['totalCompra']-resumen['reteRenta'],2)
        resumen['totalLetras']=numero_to_letras(round(resumen['totalPagar'],2))
        ##resumen['totalIva']=round(f.iva,2)
        resumen['pagos']=f.get_pagos()
        resumen['observaciones']=f.observaciones
        if f.invoice_payment_term_id.fe_condicion_id:
            resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        else:
            resumen['condicionOperacion']=2
        return resumen





##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   DONACION
##-----------------------------------------------------------------------------------------------------------------------------------------------------------        
    def get_donacion(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_donacion()
        dic['donatario']=f.get_emisor_donacion()
        dic['donante']=f.get_receptor_donacion()
        dic['cuerpoDocumento']=f.get_cuerpo_donacion()
        dic['resumen']=f.get_resumen_donacion()
        dic['otrosDocumentos']=f.get_doc_asociados_donacion()
        dic['apendice']=None
        return dic


    def get_emisor_donacion(self):
        self.ensure_one()
        f=self
        emisor={}
        #emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nrc']=f.company_id.partner_id.nrc.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['codActividad']=f.company_id.partner_id.fe_actividad_id.codigo
        emisor['descActividad']=f.company_id.partner_id.fe_actividad_id.name
        emisor['nombreComercial']=None
        emisor['nrc']=None
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['direccion']=f.get_direccion(f.company_id.partner_id)
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codEstableMH']=None
        emisor['codEstable']=None
        emisor['codPuntoVentaMH']=None
        emisor['codPuntoVenta']=None
        emisor['tipoDocumento']='36'
        emisor['numDocumento']=f.company_id.partner_id.nit.replace('-','')
        return emisor
    
    
    def get_identificacion_donacion(self):        
        self.ensure_one()
        f=self
        if not f.uuid:
            f.uuid=str(uuid.uuid4()).upper()
            f.control=f.tipo_documento_id.fe_tipo_doc_id.sequencia_id.next_by_id()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        identificacion['numeroControl']=f.control
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        fecha=f.date_confirm
        identificacion['fecEmi']=fecha.strftime('%Y-%m-%d')
        identificacion['horEmi']=fecha.strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'        
        return identificacion

    def get_receptor_donacion(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            if f.partner_id.x_dui:
                receptor['tipoDocumento']='13'
                receptor['numDocumento']=f.partner_id.x_dui.replace('-','')
            else:
                receptor['tipoDocumento']='36'
                receptor['numDocumento']=f.partner_id.nit.replace('-','')
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['codPais'] = f.partner_id.country_id.fe_codigo
            receptor['correo']=f.partner_id.email
            receptor['nrc']=f.partner_id.nrc.replace('-','')
            receptor['codDomiciliado']=int(f.partner_id.fe_domicilio_id.codigo)
            #receptor['nombreComercial']=None
            #receptor['tipoEstablecimiento']=f.partner_id.fe_establecimiento_id.codigo
            return receptor
        else:
            return None
    
   
    def get_doc_asociados_donacion(self):
        self.ensure_one()
        lista=[]
        for l in self.doc_asociados:
            dic={}
            dic['codDocAsociado']=int(l.fe_doc_asociado_id.codigo)
            dic['descDocumento']=l.name
            dic['detalleDocumento']=l.descripcion
            lista.append(dic)
        return lista



    def get_cuerpo_donacion(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=f.extra_discount
        f.exentas_des=0
        f.nosujetas_des=0
        f.retencion=0
        f.percepcion=0
        f.isr=0
        f.iva=0
        lista=[]
        i=1
        for l in f.invoice_line_ids:
            dic={}
            dic['numItem']=i
            #if l.product_id and l.product_id.fe_tipo_item_id:
            #    dic['tipoItem']=int(l.product_id.fe_tipo_item_id.codigo)
            #else:
            #    dic['tipoItem']=1
            dic['cantidad']=l.quantity
            dic['codigo']=l.product_id.default_code if l.product_id.default_code else 'NA'
            if l.uom_id.fe_unidad_id:
                dic['uniMedida']=int(l.uom_id.fe_unidad_id.codigo)
            else:
                dic['uniMedida']=59
            dic['descripcion']=l.name
            dic['valorUni']=l.price_unit
            dic['depreciacion']=l.depreciacion
            dic['tipoDonacion']=int(l.tipo_donacion.codigo)

            descuento=l.discount/100
            valor_con_descuento=1-descuento
            
            #dic['montoDescu']=(l.price_unit*l.quantity*descuento)
            iva=False
            ivap=0
            exento=True
            nosujeto=False
            retencion=False
            persepcion=False
            isr=False
            tributos=[]
            for t in l.invoice_line_tax_ids:
                iva=True if t.tax_group_id.name=='iva' else False
                ivap=t.amount/100 if t.tax_group_id.name=='iva' else ivap
                exento=True if t.tax_group_id.name=='exento' else False
                nosujeto=True if t.tax_group_id.name=='nosujeto' else False
                retencion=True if t.tax_group_id.name=='retencion' else False
                persepcion=True if t.tax_group_id.name=='persepcion' else False
                isr=True if t.tax_group_id.name=='isr' else False

                f.retencion+=((l.price_unit*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.name=='retencion' else 0
                f.percepcion+=((l.price_unit*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.name=='persepcion' else 0
                f.isr+=((l.price_unit*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.name=='isr' else 0
                if t.fe_tributo_id:
                    tributos.append(t.fe_tributo_id.codigo)
            dic['valor']=l.price_subtotal
            f.nosujetas+=l.price_subtotal
            lista.append(dic)
            i+=1
        return lista

    def get_resumen_donacion(self):
        self.ensure_one()
        f=self
        resumen={}
        #resumen['descu']=0
        #resumen['totalDescu']=round(f.nosujetas_des+f.exentas_des+f.gravadas_des,2)
        resumen['valorTotal']=f.nosujetas
        #resumen['ivaRete1']=round(f.retencion,2)
        #resumen['reteRenta']=round(abs(f.isr),2)
        #resumen['totalCompra']=f.nosujetas
        #resumen['totalPagar']=round(resumen['totalCompra']-resumen['reteRenta'],2)
        resumen['totalLetras']=numero_to_letras(round(resumen['valorTotal'],2))
        resumen['pagos']=f.get_pagos()
        #resumen['observaciones']=f.observaciones
        #if f.payment_term_id.fe_condicion_id:
        #    resumen['condicionOperacion']=int(f.payment_term_id.fe_condicion_id.codigo)
        #else:
        #    resumen['condicionOperacion']=2
        return resumen




##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   NOTA DEBITO
##-----------------------------------------------------------------------------------------------------------------------------------------------------------        
    def get_nd(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_nd()
        dic['documentoRelacionado']=f.get_relacionado_nd()
        dic['emisor']=f.get_emisor_nd()
        dic['receptor']=f.get_receptor_nd()
        #dic['otrosDocumentos']=f.get_otros()
        dic['ventaTercero']=f.get_terceros()
        dic['cuerpoDocumento']=f.get_cuerpo_nd()
        dic['resumen']=f.get_resumen_nd()
        dic['extension']=f.get_extension()
        dic['apendice']=None
        return dic

    def get_emisor_nd(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nrc']=f.company_id.partner_id.nrc.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['codActividad']=f.company_id.partner_id.fe_actividad_id.codigo
        emisor['descActividad']=f.company_id.partner_id.fe_actividad_id.name
        emisor['nombreComercial']=None
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['direccion']=f.get_direccion(f.company_id.partner_id)
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        #emisor['codEstableMH']=None
        #emisor['codEstable']=None
        #emisor['codPuntoVentaMH']=None
        #emisor['codPuntoVenta']=None
        return emisor
    
    def get_relacionado_nd(self):
        self.ensure_one()
        f=self
        if f.doc_relacionado:
            docs=[]
            doc={}
            doc['tipoDocumento']=f.doc_relacionado.tipo_documento_id.fe_tipo_doc_id.codigo
            doc['tipoGeneracion']=2 if f.doc_relacionado.uuid else 1
            doc['numeroDocumento']=f.doc_relacionado.uuid if f.doc_relacionado.uuid else f.doc_relacionado.doc_numero
            doc['fechaEmision']=f.doc_relacionado.invoice_date.strftime('%Y-%m-%d')
            docs.append(doc)
            return docs
        else:
            return None

    def get_identificacion_nd(self):        
        self.ensure_one()
        f=self
        if not f.uuid and not f.proforma:
            f.uuid=str(uuid.uuid4()).upper()
            if f.tipo_documento_id.sequencia_id:
                f.control=f.tipo_documento_id.sequencia_id.next_by_id()
            else:
                f.control=f.tipo_documento_id.fe_tipo_doc_id.sequencia_id.next_by_id()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        #identificacion['numeroControl']='DTE-'+f.tipo_documento_id.fe_tipo_doc_id.codigo.zfill(2)+'-00000000-'+str(f.id).rjust(15,'0')
        identificacion['numeroControl']=f.control
        #f.control=identificacion['numeroControl']
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        identificacion['tipoContingencia']=None if not f.contingencia else int(f.contingencia.fe_contingencia_id.codigo)
        identificacion['motivoContin']=None if not f.contingencia else int(f.contingencia.motivo)
        if not f.proforma:
            identificacion['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%H:%M:%S')
        else:
            identificacion['fecEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'        
        return identificacion

    def get_receptor_nd(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
           
            receptor['nit']=f.partner_id.nit.replace('-','') if f.partner_id.nit else None
            receptor['nrc']=f.partner_id.nrc.replace('-','') if f.partner_id.nrc else None
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            receptor['nombreComercial']=f.partner_id.comercial
            receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['correo']=f.partner_id.email
            return receptor
        else:
            return None

    def get_cuerpo_nd(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=f.extra_discount
        f.exentas_des=0
        f.nosujetas_des=0
        f.retencion=0
        f.percepcion=0
        f.isr=0
        f.iva=0
        lista=[]
        i=1
        for l in f.invoice_line_ids:
            if l.price_total>0:
                dic={}
                dic['numItem']=i
                if l.product_id and l.product_id.fe_tipo_item_id:
                    dic['tipoItem']=int(l.product_id.fe_tipo_item_id.codigo)
                else:
                    dic['tipoItem']=1
                dic['numeroDocumento']=f.doc_relacionado.uuid if f.doc_relacionado.uuid else f.doc_relacionado.doc_numero
                dic['cantidad']=l.quantity
                dic['codigo']=l.product_id.default_code
                dic['codTributo']=None
                if l.product_uom_id.fe_unidad_id:
                    dic['uniMedida']=int(l.product_uom_id.fe_unidad_id.codigo)
                else:
                    dic['uniMedida']=59
                dic['descripcion']=l.name
                

                descuento=l.discount/100
                valor_con_descuento=1-descuento
                
                dic['montoDescu']=0
                iva=False
                ivap=0
                exento=True
                nosujeto=False
                retencion=False
                persepcion=False
                isr=False
                tributos=[]
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                    if iva==True:
                        incluido=t.price_include
                        price_unit=l.price_unit/(1+ivap)
                    if incluido:
                        price_unit=l.price_unit
                        price_unit_notax=l.price_unit/(1+ivap)
                        ivaitem=(l.price_unit*valor_con_descuento)-(l.price_unit/(1+ivap))
                    else:
                        price_unit=l.price_unit*(1+ivap)
                        price_unit_notax=l.price_unit
                        ivaitem=(l.price_unit*valor_con_descuento)*ivap
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                    retencion=True if t.tax_group_id.code=='retencion' else False
                    persepcion=True if t.tax_group_id.code=='persepcion' else False
                    isr=True if t.tax_group_id.code=='isr' else False

                    f.retencion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='retencion' else 0
                    f.percepcion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='persepcion' else 0
                    f.isr+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='isr' else 0
                    if t.fe_tributo_id:
                        tributos.append(t.fe_tributo_id.codigo)
                dic['precioUni']=round(price_unit_notax,6)
                if iva or retencion or persepcion:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=0
                    dic['ventaGravada']=round((price_unit_notax*l.quantity*valor_con_descuento),6)
                    dic['montoDescu']= round(price_unit_notax*l.quantity*descuento,6)
                    f.gravadas_linea_des+=dic['montoDescu']
                elif exento:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=round((price_unit_notax*l.quantity*valor_con_descuento),6)
                    dic['ventaGravada']=0
                    dic['montoDescu']= round(price_unit_notax*l.quantity*descuento,6)
                    f.exentas_linea_des+=dic['montoDescu']
                elif nosujeto:
                    dic['ventaNoSuj']=round((price_unit_notax*l.quantity*valor_con_descuento),6)
                    dic['ventaExenta']=0
                    dic['ventaGravada']=0
                    dic['montoDescu']= round(price_unit_notax*l.quantity*descuento,6)
                    f.nosujetas_linea_des+=dic['montoDescu']
                else:
                    dic['ventaNoSuj']=0
                    dic['ventaExenta']=0
                    dic['ventaGravada']=0
                f.gravadas+=dic['ventaGravada']
                f.exentas+=dic['ventaExenta']
                f.nosujetas+=dic['ventaNoSuj']
                if len(tributos)>0:
                    dic['tributos']=tributos
                else:
                    dic['tributos']=None
                #dic['psv']=0
                #dic['noGravado']=0
                f.iva+=(round((price_unit_notax*l.quantity*valor_con_descuento)*(ivap),6))
                lista.append(dic)
                i+=1
            else:
                descuento_global+=(l.price_total*-1)
                iva=False
                exento=True
                nosujeto=False
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                if iva or retencion or persepcion:
                    f.gravadas_des+=(l.price_subtotal*-1)
                elif exento:
                    f.exentas_des+=(l.price_subtotal*-1)
                elif nosujeto:
                    f.nosujetas_des+=(l.price_subtotal*-1)
                iva=False
                ivap=0
                exento=True
                nosujeto=False
                retencion=False
                persepcion=False
                isr=False
                tributos=[]
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                    if iva==True:
                        incluido=t.price_include
                        price_unit=price_unit/(1+ivap)
                    if incluido:
                        price_unit=l.price_unit
                        price_unit_notax=l.price_unit/(1+ivap)
                    else:
                        price_unit=l.price_unit*(1+ivap)
                        price_unit_notax=l.price_unit
                f.iva+=(round((price_unit_notax*l.quantity)*(ivap),6))
                f.iva_des+=(round((price_unit_notax*l.quantity*-1)*(ivap),6))
            
        return lista

    def get_resumen_nd(self):
        self.ensure_one()
        f=self
        resumen={}
        resumen['totalNoSuj']=round(f.nosujetas,2)
        resumen['totalExenta']=round(f.exentas,2)
        resumen['totalGravada']=round(f.gravadas,2)
        resumen['subTotalVentas']=round(f.nosujetas+f.exentas+f.gravadas,2)
        total=resumen['subTotalVentas']+f.iva
        resumen['descuNoSuj']=round(f.nosujetas_des,2)
        resumen['descuExenta']=round(f.exentas_des,2)
        resumen['descuGravada']=round(f.gravadas_des,2)
        resumen['totalDescu']=round(f.nosujetas_des+f.exentas_des+f.gravadas_des+f.exentas_linea_des+f.nosujetas_linea_des+f.gravadas_linea_des,2)
        #resumen['porcentajeDescuento']=round((resumen['totalDescu']/resumen['subTotalVentas'])*100,2)
        resumen['numPagoElectronico']=None
        tributos=[]
        for l in f.invoice_line_ids:
            for t in l.tax_ids:
                if t.fe_tributo_id:
                    if  t.fe_tributo_id.codigo!='0':
                            if not t.id in tributos:                            
                                tributos.append(t.id)
        if len(tributos)>0:
            tributosmh=[]
            for t in tributos:
                tmh={}
                tax=self.env['account.tax'].browse(t)
                tmh['codigo']=tax.fe_tributo_id.codigo
                tmh['descripcion']=tax.fe_tributo_id.name
                valor=0
                for l in f.line_ids:
                   if l.tax_line_id and l.tax_line_id.id==t:
                      valor=l.credit-l.debit if l.credit>l.debit else l.debit-l.credit
                tmh['valor']=round(valor,2)
                tributosmh.append(tmh)
            resumen['tributos']=tributosmh
        else:
            resumen['tributos']=None
        resumen['subTotal']=round(resumen['subTotalVentas']-resumen['descuNoSuj']-resumen['descuExenta']-resumen['descuGravada'],2)
        resumen['ivaPerci1']=round(f.percepcion*-1,2)
        resumen['ivaRete1']=round(f.retencion*-1,2)
        resumen['reteRenta']=round(f.isr,2)
        resumen['montoTotalOperacion']=round(resumen['subTotal']+f.iva,2)
        #resumen['totalNoGravado']=0
        #resumen['totalPagar']=round(resumen['montoTotalOperacion'],2)
        resumen['totalLetras']=numero_to_letras(round(resumen['montoTotalOperacion'],2))
        ##resumen['totalIva']=round(f.iva,2)
        #resumen['saldoFavor']=0
        if f.invoice_payment_term_id.fe_condicion_id:
            resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        else:
            resumen['condicionOperacion']=2
        return resumen






##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   COMUNES
##-----------------------------------------------------------------------------------------------------------------------------------------------------------        
    

    
    def get_documento_relacionado(self):
        return None

    def get_emisor(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nrc']=f.company_id.partner_id.nrc.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['codActividad']=f.company_id.partner_id.fe_actividad_id.codigo
        emisor['descActividad']=f.company_id.partner_id.fe_actividad_id.name
        emisor['nombreComercial']=None
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['direccion']=f.get_direccion(f.company_id.partner_id)
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codEstableMH']=None
        emisor['codEstable']=None
        emisor['codPuntoVentaMH']=None
        emisor['codPuntoVenta']=None
        
        return emisor
    
    def get_direccion(self,partner):
        self.ensure_one()
        f=self
        direccion={}
        direccion['departamento']=partner.fe_municipio_id.departamento_id.code
        direccion['municipio']=partner.fe_municipio_id.codigo
        direccion['complemento']=partner.street
        return direccion


        

    def get_otros(self):
        return None
    
    def get_terceros(self):
        return None

    def get_cuerpo(self):
        self.ensure_one()
        f=self
        if f.tipo_documento_id.codigo=='Factura':
            return f.get_cuerpo_fac()
        elif f.tipo_documento_id.codigo=='CCF':
            return f.get_cuerpo_ccf()
        else:
            return None


    


    def get_resumen(self):
        self.ensure_one()
        f=self
        if f.tipo_documento_id.codigo=='Factura':
            return f.get_resumen_fac()
        elif f.tipo_documento_id.codigo=='CCF':
            return f.get_resumen_ccf()
        else:
            return None



    
    

    def get_pagos(self):
        return None

    def get_extension(self):
        self.ensure_one()
        f=self
        extension={}
        if f.entrega:
            extension['nombEntrega']=f.entrega
        if f.doc_entrega:
            extension['docuEntrega']=f.doc_entrega
        if f.recibe:
            extension['nombRecibe']=f.recibe
        if f.doc_recibe:
            extension['docuRecibe']=f.doc_recibe
        if f.observaciones:
            extension['observaciones']=f.observaciones
        if f.placa:
            extension['placaVehiculo']=f.placa
        if len(extension)==0:
            return None
        else:
            return extension
    

##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   FACTURA EXPORTACION
##-----------------------------------------------------------------------------------------------------------------------------------------------------------
    def get_exp(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_export()
        #dic['documentoRelacionado']=None
        dic['emisor']=f.get_emisor_export()
        dic['receptor']=f.get_receptor_export()
        dic['otrosDocumentos']=f.get_otros()
        dic['ventaTercero']=f.get_terceros()
        dic['cuerpoDocumento']=f.get_cuerpo_exp()
        dic['resumen']=f.get_resumen_exp()
        #dic['extension']=f.get_extension_exp()
        #dic['extension']=f.get_extension()
        dic['apendice']=None
        return dic
    
    def get_emisor_export(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nrc']=f.company_id.partner_id.nrc.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['codActividad']=f.company_id.partner_id.fe_actividad_id.codigo
        emisor['descActividad']=f.company_id.partner_id.fe_actividad_id.name
        emisor['nombreComercial']=None
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['direccion']=f.get_direccion(f.company_id.partner_id)
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codEstableMH']=None
        emisor['codEstable']=None
        emisor['codPuntoVentaMH']=None
        emisor['codPuntoVenta']=None
        if f.tipo_documento_id.fe_tipo_doc_id.codigo=='11':
            if f.sv_fe_tipo_itemexpor_id:
                emisor['tipoItemExpor']= int(f.sv_fe_tipo_itemexpor_id.codigo)
            if f.sv_fe_tipo_itemexpor_id:
                emisor['recintoFiscal'] = f.sv_fe_resinto_id.codigo
            else:
                emisor['recintoFiscal'] = None
            if f.sv_fe_regimen_id:
                emisor['regimen'] = f.sv_fe_regimen_id.codigo
            else:
                emisor['regimen'] = None
        #raise UserError(str(emisor))
        return emisor

    def get_identificacion_export(self):        
        self.ensure_one()
        f=self
        if not f.uuid and not f.proforma:
            f.uuid=str(uuid.uuid4()).upper()
            if f.tipo_documento_id.sequencia_id:
                f.control=f.tipo_documento_id.sequencia_id.next_by_id()
            else:
                f.control=f.tipo_documento_id.fe_tipo_doc_id.sequencia_id.next_by_id()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        identificacion['numeroControl']=f.control
        #identificacion['numeroControl']
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        
        identificacion['tipoContingencia']=None if not f.contingencia else int(f.contingencia.fe_contingencia_id.codigo)
        #identificacion['motivoContin']=None if not f.contingencia else int(f.contingencia.motivo)
        #identificacion['motivoContin']=None
        if not f.proforma:
            identificacion['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%H:%M:%S')
        else:
            identificacion['fecEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%Y-%m-%d')
            identificacion['horEmi']=(datetime.now()+timedelta(hours=-6)).strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'      
        identificacion['motivoContigencia'] = None  
        return identificacion

    def get_receptor_export(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            receptor['tipoDocumento']='37'
            receptor['numDocumento']=f.partner_id.vat
            
            if f.partner_id.comercial:
                 receptor['nombreComercial']=f.partner_id.comercial
            else:
                 receptor['nombreComercial'] = None
            receptor['nombrePais'] = f.partner_id.country_id.name
            receptor['codPais'] = f.partner_id.country_id.fe_codigo
            receptor['tipoPersona'] = int(f.partner_id.fe_tipo_persona_id.codigo )  
            receptor['complemento']= f.partner_id.street
            receptor['nombre']=f.partner_id.name
            #receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            #receptor['nombreComercial']=None
            #receptor['tipoEstablecimiento']=f.fe_establecimiento_id.codigo
            #receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['correo']=f.partner_id.email
           
            #receptor['codEstableMH']=None
            #receptor['codEstable']=None
            #receptor['codPuntoVentaMH']=None
            #receptor['codPuntoVenta']=None
            #receptor['nombrePais'] = f.partner_id.fe_country_id.name

            
            return receptor
        else:
            return None

    def get_cuerpo_exp(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=f.extra_discount
        f.exentas_des=0
        f.nosujetas_des=0
        f.gravadas_linea_des=0
        f.exentas_linea_des=0
        f.nosujetas_linea_des=0
        f.retencion=0
        f.percepcion=0
        f.isr=0
        f.iva=0
        lista=[]
        exportacion = 0
        i=1
        incluido=False
        descuento_global=0.0
        for l in f.invoice_line_ids:
            if l.price_total>0:
                dic={}
                dic['numItem']=i
                #if l.product_id and l.product_id.fe_tipo_item_id:
                    #dic['tipoItem']=int(l.product_id.fe_tipo_item_id.codigo)
                #else:
                    #dic['tipoItem']=1
                #dic['numeroDocumento']=None
                dic['cantidad']=l.quantity
                dic['codigo']=l.product_id.default_code
                #dic['codTributo']=None
                if l.product_uom_id.fe_unidad_id:
                    dic['uniMedida']=int(l.product_uom_id.fe_unidad_id.codigo)
                else:
                    dic['uniMedida']=59
                dic['descripcion']=l.name
                dic['precioUni']=l.price_unit

                descuento=l.discount/100
                valor_con_descuento=1-descuento
                
                dic['montoDescu']=(l.price_unit*l.quantity*descuento)
                iva=False
                ivap=0
                ivaitem=0
                price_unit_notax=0
                exento=True
                nosujeto=False
                retencion=False
                persepcion=False
                isr=False
                tributos=[]
                price_unit=l.price_unit
                
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    ivap=t.amount/100 if t.tax_group_id.code=='iva' else ivap
                    if iva==True:
                        incluido=t.price_include
                        price_unit=price_unit/(1+ivap)
                    if incluido:
                        price_unit=l.price_unit
                        price_unit_notax=l.price_unit/(1+ivap)
                        ivaitem=(l.price_unit*valor_con_descuento)-(l.price_unit/(1+ivap))
                    else:
                        price_unit=l.price_unit*(1+ivap)
                        price_unit_notax=l.price_unit
                        ivaitem=(l.price_unit*valor_con_descuento)*ivap
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                    retencion=True if t.tax_group_id.code=='retencion' else False
                    persepcion=True if t.tax_group_id.code=='persepcion' else False
                    isr=True if t.tax_group_id.code=='isr' else False

                    f.retencion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='retencion' else 0
                    f.percepcion+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='persepcion' else 0
                    f.isr+=((price_unit_notax*l.quantity*valor_con_descuento)*(t.amount/100)) if t.tax_group_id.code=='isr' else 0
                    if t.fe_tributo_id:
                        if  t.fe_tributo_id.codigo!='20':
                            tributos.append(t.fe_tributo_id.codigo)
        
                    #dic['ventaNoSuj']=0
                    #dic['ventaExenta']=0
                    dic['ventaGravada']=round((price_unit*l.quantity*valor_con_descuento)*(1),2)
                    dic['precioUni']=round(price_unit,2)
                    f.gravadas_linea_des+=dic['montoDescu']
                    f.gravadas+=dic['ventaGravada']
                
            
                #f.nosujetas+=dic['ventaNoSuj']
                if len(tributos)>0:
                    dic['tributos']=tributos
                else:
                    dic['tributos']=None
                #dic['psv']=0
                dic['noGravado']=0

                lista.append(dic)
                i+=1
            else:
                descuento_global+=l.price_subtotal
                iva=False
                exento=True
                nosujeto=False
                for t in l.tax_ids:
                    iva=True if t.tax_group_id.code=='iva' else False
                    exento=True if t.tax_group_id.code=='exento' else False
                    nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                if iva or retencion or persepcion:
                    f.gravadas_des+=(l.price_total*-1)
                elif exento:
                    f.gravadas_des+=(l.price_total*-1)
                elif nosujeto:
                    f.gravadas_des+=(l.price_total*-1)
                else:
                    f.gravadas_des+=(l.price_total*-1)
            
        return lista
    
    def get_extension_exp(self):
        self.ensure_one()
        f=self
        extension={}
        if f.entrega:
            extension['nombEntrega']=f.entrega
        if f.doc_entrega:
            extension['docuEntrega']=f.doc_entrega
        if f.recibe:
            extension['nombRecibe']=f.recibe
        if f.doc_recibe:
            extension['docuRecibe']=f.doc_recibe
        if f.observaciones:
            extension['observaciones']=f.observaciones
        if f.placa:
            extension['placaVehiculo']=f.placa
        if len(extension)==0:
            return None
        else:
            return extension

    def get_resumen_exp(self):
        self.ensure_one()
        f=self
        resumen={}
        #resumen['totalNoSuj']=round(f.nosujetas,2)
        #resumen['totalExenta']=round(f.exentas,2)
        resumen['totalGravada']=round(f.gravadas,2)
        #resumen['subTotalVentas']=round(f.nosujetas+f.exentas+f.gravadas,2)
        #resumen['descuNoSuj']=round(f.nosujetas_des,2)
        #resumen['descuExenta']=round(f.exentas_des,2)
        #resumen['descuGravada']=round(f.gravadas_des,2)
        resumen['porcentajeDescuento'] = 0
        resumen['totalDescu']=round(f.gravadas_des+f.gravadas_linea_des,2)
        #resumen['totalDescu']=round(f.nosujetas_des+f.exentas_des+f.gravadas_des,2)
        resumen['porcentajeDescuento']=round((resumen['totalDescu']/resumen['totalGravada'])*100,2)
        tributos=[]
        for l in f.invoice_line_ids:
            for t in l.tax_ids:
                if t.fe_tributo_id:
                    if  t.fe_tributo_id.codigo!='20':
                        if not t.fe_tributo_id.codigo in tributos:
                            tributos.append(t.fe_tributo_id.codigo)

        #resumen['tributos']=tributos
        #resumen['subTotal']=round(resumen['subTotalVentas']-resumen['totalDescu'],2)

        #resumen['ivaRete1']=round(f.retencion,2)
        #resumen['reteRenta']=round(f.isr,2)
        resumen['observaciones']=f.observaciones
        
        resumen['totalNoGravado']=0
       
       
        #resumen['porcentajeDescuento'] = 
        if f.invoice_incoterm_id:
            resumen['codIncoterms'] = f.invoice_incoterm_id.fe_incoterm_id.codigo
        else:
            resumen['codIncoterms'] = None
        #resumen['totalIva']=round(f.iva,2)
        #resumen['saldoFavor']=0
        if f.invoice_payment_term_id.fe_condicion_id:
            resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        else:
            resumen['condicionOperacion']=2
        resumen['pagos']=f.get_pagos()
        resumen['numPagoElectronico']=None
        resumen['flete']= f.flete
        resumen['descuento']=f.gravadas_des
        resumen['seguro']= f.sv_fe_seguro
        resumen['montoTotalOperacion']=round(resumen['totalGravada']-resumen['descuento'],2)
        resumen['descIncoterms'] = f.invoice_incoterm_id.name
        resumen['totalPagar']=round(resumen['montoTotalOperacion']+f.flete+f.sv_fe_seguro,2)
        resumen['totalLetras']=numero_to_letras(round(resumen['totalPagar'],2))
        #resumen['codIncoterms']= f.
        #raise UserError(str(f.gravadas_des))
        return resumen        








class sv_fe_move_picking(models.Model):
    _inherit='stock.picking'
    uuid=fields.Char("Codigo de Generacion",copy=False)
    sello=fields.Char("Sello",copy=False)
    control=fields.Char("Numero de control",copy=False)
    reversion_sello=fields.Char("Sello",copy=False)
    reversion_uuid=fields.Char("UUID",copy=False)
    date_confirm=fields.Datetime('Fecha de confirmacion',copy=False)


    entrega=fields.Char("Entrega",copy=False)
    doc_entrega=fields.Char("Doc. Entrega",copy=False)
    recibe=fields.Char("Recibe",copy=False)
    doc_recibe=fields.Char("Doc. Recibe",copy=False)
    observaciones=fields.Char("Observaciones",copy=False)

    doc_json=fields.Text("Doc JSON",copy=False)
    doc_firmado=fields.Text("Doc. Firmado",copy=False)
    doc_sellado=fields.Text("Doc. Sellado",copy=False)
    doc_respuesta=fields.Text("Respuesta",copy=False)

    reversion_json=fields.Text("Doc JSON",copy=False)
    reversion_firmado=fields.Text("Doc. Firmado",copy=False)
    reversion_sellado=fields.Text("Doc. Sellado",copy=False)
    reversion_respuesta=fields.Text("Reversión respuesta",copy=False)
    reversion_motivo=fields.Char("Motivo",copy=False)
    reversion_responsable=fields.Char("Responsable",copy=False)
   
    reversion_responsable_tipo=fields.Char('Tipo de documento Responsable',copy=False)
    reversion_responsable_doc=fields.Char("Doc del Responsable",copy=False)
    reversion_solicita=fields.Char("Nombre solicitante",copy=False)
    reversion_solicita_tipo=fields.Char("Tipo Doc solicitante",copy=False)    
    reversion_solicita_doc=fields.Char("Doc solicitante",copy=False)
    reversion_responsable_tipo_id=fields.Many2one(comodel_name='sv_fe.doc_identificacion',string='Tipo documento')
    reversion_solicita_tipo_id=fields.Many2one(comodel_name='sv_fe.doc_identificacion',string='Tipo documento')
    
    dte_estado=fields.Char("Estado del DTE",copy=False)
    dte_error=fields.Char("Error del DTE",copy=False)
    dte_qr=fields.Char(string='QR',compute='get_qr',store=False)
    tipo_documento_id=fields.Many2one(comodel_name='odoosv.fiscal.document',store=True,string="Tipo de documento")
    fe_tipo_doc_id=fields.Many2one(comodel_name='sv_fe.tipo_doc',related='tipo_documento_id.fe_tipo_doc_id',store=True,string="Tipo de documento")
    fe_codigo=fields.Char(string='Codigo tipo doc',related='fe_tipo_doc_id.codigo',store=True)
    fe_transmision_id=fields.Many2one(comodel_name='sv_fe.transmision',string='Modelo de Transmision')
    fe_ambiente_id=fields.Many2one(comodel_name='sv_fe.ambiente',string='Ambiente')
    fe_remision_id=fields.Many2one(comodel_name='sv_fe.remision',string="Remision por")
    monto_total=fields.Float("Monto total")
    currency_id=fields.Many2one(comodel_name='res.currency',related='company_id.currency_id',string="Moneda")


    

    def get_json(self):
        for r in self:
            return json.loads(r.doc_json)

    @api.depends('sello','dte_estado')
    def get_qr(self):
        for r in self:
            res=''
            #if r.move_type in ('out_invoice','out_refund','in_invoice','in_refound',''):
            ambiente='00'
            if r.fe_ambiente_id:
                ambiente=r.fe_ambiente_id.codigo
            else:
                ambiente=r.company_id.fe_ambiente_id.codigo
            res='https://admin.factura.gob.sv/consultaPublica%3Fambiente='+ambiente+'%26codGen='+r.uuid+'%26fechaEmi='+(r.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
            #res='https://admin.factura.gob.sv/consultaPublica?ambiente=01&codGen='+r.uuid+'&echaEmi='+(r.date_confirm).strftime('%Y-%m-%d')
            r.dte_qr=res

    
    def solo_imprimir(self):
        self.ensure_one()
        self.generar_solo_fe()
        return self.env.ref('sv_fe.dte_report_picking').report_action(self)

    def generar_solo_fe(self):
        self.ensure_one()
        f=self
        if not f.date_confirm:
            f.date_confirm=datetime.now()
        firma={}
        firma['nit']=f.company_id.partner_id.nit.replace('-','')
        firma['passwordPri']=f.company_id.fe_ambiente_id.llave_privada
        firma['dteJson']=f.get_nr()
        #f.doc_numero=f.control
        encabezado = {"content-type": "application/JSON","User-Agent":"Odoo/16"}
        json_datos = json.dumps(firma)
        json_datos=json_datos.replace('None','null')
        json_datos=json_datos.replace('False','null')
        json_datos=json_datos.replace('false','null')
        json_datos_cliente=json.dumps( firma['dteJson'])
        json_datos_cliente=json_datos_cliente.replace('None','null')
        json_datos_cliente=json_datos_cliente.replace('False','null')
        json_datos_cliente=json_datos_cliente.replace('false','null')
        f.doc_json=json_datos_cliente
        
    def generar_fe(self,contingencia=False):
        self.ensure_one()
        f=self

        if not contingencia:
            f.fe_transmision_id=self.env.ref('sv_fe.svfe_transmision_1').id
            f.fe_ambiente_id=f.company_id.fe_ambiente_id.id
        else:
            f.fe_transmision_id=self.env.ref('sv_fe.svfe_transmision_2').id
        f.date_confirm=datetime.now()
        if not f.partner_id:
            f.partner_id=f.company_id.partner_id.id

        firma={}
        firma['nit']=f.company_id.partner_id.nit.replace('-','')
        firma['passwordPri']=f.company_id.fe_ambiente_id.llave_privada
        firma['dteJson']=f.get_nr()
        #f.doc_numero=f.control
        encabezado = {"content-type": "application/JSON","User-Agent":"Odoo/16"}
        json_datos = json.dumps(firma)
        json_datos=json_datos.replace('None','null')
        json_datos=json_datos.replace('False','null')
        json_datos=json_datos.replace('false','null')
        json_datos_cliente=json.dumps( firma['dteJson'])
        json_datos_cliente=json_datos_cliente.replace('None','null')
        json_datos_cliente=json_datos_cliente.replace('False','null')
        json_datos_cliente=json_datos_cliente.replace('false','null')
        f.doc_json=json_datos_cliente
        result = requests.post(f.company_id.fe_ambiente_id.firmador,data=json_datos, headers=encabezado)
        respuesta=json.loads(result.text)
        if respuesta['status']=="OK":
            body=respuesta["body"]
            f.doc_firmado=body
            encabezado={}
            encabezado['Authorization']=f.company_id.fe_ambiente_id.get_token()
            encabezado['User-Agent']="Odoo/16"
            encabezado['content-type']="application/JSON"
            dic={}
            dic['ambiente']=f.company_id.fe_ambiente_id.codigo
            dic['idEnvio']=f.id
            dic['version']=f.tipo_documento_id.version
            dic['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
            dic['documento']=body
            dic['codigoGeneracion']=f.uuid
            json_datos = json.dumps(dic)
            json_datos=json_datos.replace('None','null')
            json_datos=json_datos.replace('False','null')
            #raise UserError(str(encabezado)+'------'+json_datos)
            print('---------------------------------------------------------------------------------------------------------')
            print(str(encabezado))
            print('------------------------------')
            print(str(json_datos))
            print('----------------------------------------------------------------------------------------------------------')
            result=requests.post(f.company_id.fe_ambiente_id.url+'/fesv/recepciondte',data=json_datos, headers=encabezado)
            print(str(result))
            f.doc_respuesta=result.text
            try:
                respuesta=json.loads(result.text)
                f.dte_estado=respuesta['estado']
                if respuesta['estado']=='PROCESADO':
                    f.sello=respuesta['selloRecibido']
                else:
                    f.dte_error=respuesta['observaciones']
            except:
                print('Error')
  

    def revertir_fe(self):
        self.ensure_one()
        f=self
        firma={}
        firma['nit']=f.company_id.partner_id.nit.replace('-','')
        firma['passwordPri']=f.company_id.fe_ambiente_id.llave_privada
        firma['dteJson']=f.get_reversion()       
        f.reversion_json=firma['dteJson']
        encabezado = {"content-type": "application/JSON","User-Agent":"Odoo/16"}
        json_datos = json.dumps(firma)
        json_datos=json_datos.replace('None','null')
        json_datos=json_datos.replace('False','null')
        #raise UserError(json_datos)
        self.env.cr.savepoint()
        result = requests.post(f.company_id.fe_ambiente_id.firmador,data=json_datos, headers=encabezado)
        respuesta=json.loads(result.text)
        #raise UserError(result.text)
        if respuesta['status']=="OK":
            body=respuesta["body"]
            f.reversion_firmado=body
            encabezado={}
            encabezado['Authorization']=f.company_id.fe_ambiente_id.get_token()
            encabezado['User-Agent']="Odoo/16"
            encabezado['content-type']="application/JSON"
            dic={}
            dic['ambiente']=f.company_id.fe_ambiente_id.codigo
            dic['idEnvio']=f.id+100000
            dic['version']=2
            dic['documento']=body
            dic['codigoGeneracion']=f.uuid
            json_datos = json.dumps(dic)
            json_datos=json_datos.replace('None','null')
            json_datos=json_datos.replace('False','null')
            print('---------------------------------------------------------------------------------------------------------')
            print(str(encabezado))
            print('------------------------------')
            print(str(json_datos))
            print('----------------------------------------------------------------------------------------------------------')
            #raise UserError(str(encabezado)+'------'+json_datos)
            self.env.cr.savepoint()
            try:
                result=requests.post(f.company_id.fe_ambiente_id.url+'/fesv/anulardte',data=json_datos, headers=encabezado)
            except:
                raise UserError('EL SITIO DEL MH NO ESTA EN LINEA')
            print(str(result))
            f.reversion_respuesta=result.text
            try:
                respuesta=json.loads(result.text)
                if respuesta['estado']=='PROCESADO':
                    f.reversion_sello=respuesta['selloRecibido']
            except:
                print('Error')
        else:
            raise UserError(respuesta['status'])

    


##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   Reversion
##-----------------------------------------------------------------------------------------------------------------------------------------------------------
    def get_reversion(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_reve()
        dic['emisor']=f.get_emisor_reve()
        dic['documento']=f.get_documento_reve()
        dic['motivo']=f.get_motivo_reve()
        return dic


    def get_emisor_reve(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['nomEstablecimiento']=f.company_id.name
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codEstableMH']=None
        emisor['codEstable']=None
        emisor['codPuntoVentaMH']=None
        emisor['codPuntoVenta']=None
        return emisor

    def get_identificacion_reve(self):        
        self.ensure_one()
        f=self
        if not f.reversion_uuid:
            f.reversion_uuid=str(uuid.uuid4()).upper()
        identificacion={}
        identificacion['version']=2
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['codigoGeneracion']=f.reversion_uuid
        fecha=datetime.now()+timedelta(hours=-6)
        identificacion['fecAnula']=fecha.strftime('%Y-%m-%d')
        identificacion['horAnula']=fecha.strftime('%H:%M:%S')
        return identificacion

    def get_receptor_reve(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            if f.partner_id.nrc and f.partner_id.nrc=='NA':
                receptor['tipoDocumento']='37'
                receptor['numDocumento']=f.partner_id.nit.replace('-','')
                receptor['nrc']=None
            else:
                if f.partner_id.nit and f.tipo_documento_id.codigo != 14:
                    receptor['tipoDocumento']='36'
                    receptor['numDocumento']=f.partner_id.nit.replace('-','')
                elif f.partner_id.dui:
                    receptor['tipoDocumento']='13'
                    receptor['numDocumento']=f.partner_id.dui.replace('-','')
                if f.partner_id.nrc:
                    receptor['nrc']=f.partner_id.nrc
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['correo']=f.partner_id.email
            return receptor
        else:
            return None

    def get_documento_reve(self):
        self.ensure_one()
        f=self
        dic={}
        dic['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        dic['codigoGeneracion']=f.uuid
        dic['selloRecibido']=f.sello
        dic['numeroControl']=f.control
        dic['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
        dic['montoIva']=0
        dic['codigoGeneracionR']=None
        if f.partner_id.nrc and f.partner_id.nrc=='NA' or f.tipo_documento_id.fe_tipo_doc_id.codigo == '11':
                if  f.tipo_documento_id.fe_tipo_doc_id.codigo == '11':
                    dic['tipoDocumento']='37'
                    dic['numDocumento']=f.partner_id.nrc.replace('-','')
        else:
            if f.partner_id.nit:
                dic['tipoDocumento']='36'
                dic['numDocumento']=f.partner_id.nit.replace('-','')
            elif f.partner_id.dui:
                dic['tipoDocumento']='13'
                dic['numDocumento']=f.partner_id.dui.replace('-','')
            else:
                dic['tipoDocumento']=''
                dic['numDocumento']=''
        dic['nombre']=f.partner_id.name
        dic['telefono']=f.partner_id.phone
        dic['correo']=f.partner_id.email
        
        return dic
    

    def get_motivo_reve(self):
        self.ensure_one()
        f=self
        dic={}
        dic['tipoAnulacion']=2
        dic['motivoAnulacion']=f.reversion_motivo
        dic['nombreResponsable']=f.reversion_responsable 
        dic['tipDocResponsable']=f.reversion_responsable_tipo_id.codigo 
        dic['numDocResponsable']=f.reversion_responsable_doc.replace('-','') if f.reversion_responsable_doc != False else None 
        dic['nombreSolicita']=f.reversion_solicita
        dic['tipDocSolicita']=f.reversion_solicita_tipo_id.codigo
        dic['numDocSolicita']=f.reversion_solicita_doc.replace('-','') if f.reversion_solicita_doc != False else None
        return dic

    def get_resumen_reve(self):
        self.ensure_one()
        f=self
        resumen={}
        #resumen['totalNoSuj']=round(f.nosujetas,2)
        #resumen['totalExenta']=round(f.exentas,2)
        #resumen['totalGravada']=round(f.gravadas,2)
        #resumen['subTotalVentas']=round(f.nosujetas+f.exentas+f.gravadas,2)
        #resumen['descuNoSuj']=round(f.nosujetas_des,2)
        #resumen['descuExenta']=round(f.exentas_des,2)
        #resumen['descuGravada']=round(f.gravadas_des,2)
        #resumen['totalDescu']=round(f.nosujetas_des+f.exentas_des+f.gravadas_des,2)
        #resumen['porcentajeDescuento']=round((resumen['totalDescu']/resumen['subTotalVentas'])*100,2)
        tributos=[]
        #resumen['tributos']=tributos
        #resumen['subTotal']=round(resumen['subTotalVentas']-resumen['totalDescu'],2)
        #resumen['ivaRete1']=round(f.retencion,2)
        #resumen['reteRenta']=round(f.isr,2)
        #resumen['montoTotalOperacion']=round(resumen['subTotal'],2)
        #resumen['totalNoGravado']=0
        #resumen['totalPagar']=round(resumen['montoTotalOperacion']-resumen['ivaRete1']-resumen['reteRenta'],2)
        #resumen['totalLetras']=numero_to_letras(round(resumen['totalPagar'],2))
        #resumen['totalIva']=round(f.iva,2)
        #resumen['saldoFavor']=0
        #if f.invoice_payment_term_id.fe_condicion_id:
        #    resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        #else:
        #    resumen['condicionOperacion']=2
        #resumen['pagos']=f.get_pagos()
        #resumen['numPagoElectronico']=None
        return resumen        




##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   NOTA DE REMISION
##-----------------------------------------------------------------------------------------------------------------------------------------------------------        
    def get_nr(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_nr()
        dic['emisor']=f.get_emisor_nr()
        dic['receptor']=f.get_receptor_nr()
        dic['cuerpoDocumento']=f.get_cuerpo_nr()
        dic['documentoRelacionado']=None
        dic['extension']=None
        dic['resumen']=f.get_resumen_nr()
        dic['apendice']=None
        dic['ventaTercero']=None
        return dic

    def get_emisor_nr(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nrc']=f.company_id.partner_id.nrc.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['codActividad']=f.company_id.partner_id.fe_actividad_id.codigo
        emisor['descActividad']=f.company_id.partner_id.fe_actividad_id.name
        emisor['nombreComercial']=None
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['direccion']=f.get_direccion(f.company_id.partner_id)
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codEstableMH']=None
        emisor['codEstable']=None
        emisor['codPuntoVentaMH']=None
        emisor['codPuntoVenta']=None
        return emisor
    
    def get_identificacion_nr(self):        
        self.ensure_one()
        f=self
        if not f.uuid:
            f.uuid=str(uuid.uuid4()).upper()
            if f.tipo_documento_id.sequencia_id:
                f.control=f.tipo_documento_id.sequencia_id.next_by_id()
            else:
                f.control=f.tipo_documento_id.fe_tipo_doc_id.sequencia_id.next_by_id()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        #identificacion['numeroControl']='DTE-'+f.tipo_documento_id.fe_tipo_doc_id.codigo.zfill(2)+'-00000000-'+str(f.id).rjust(15,'0')
        identificacion['numeroControl']=f.control
        #f.control=identificacion['numeroControl']
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        identificacion['tipoContingencia']=None
        identificacion['motivoContin']=None
        identificacion['fecEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%Y-%m-%d')
        identificacion['horEmi']=(f.date_confirm+timedelta(hours=-6)).strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'        
        return identificacion

    def get_receptor_nr(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            if f.partner_id.nit:
                receptor['tipoDocumento']='36'
                receptor['numDocumento']=f.partner_id.nit.replace('-','')
            else:
                receptor['tipoDocumento']='37'
                receptor['numDocumento']=f.partner_id.nrc.replace('-','')
            #receptor['nit']=f.partner_id.nit.replace('-','')
            receptor['nrc']=f.partner_id.nrc.replace('-','')
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            receptor['nombreComercial']=f.partner_id.name
            receptor['direccion']=f.get_direccion(f.partner_id)
            receptor['telefono']=f.partner_id.phone
            receptor['correo']=f.partner_id.email
            receptor['bienTitulo']=f.fe_remision_id.codigo
            return receptor
        else:
            return None

    def get_cuerpo_nr(self):
        self.ensure_one()
        f=self
        lista=[]
        i=1
        f.monto_total=0
        for l in f.move_ids_without_package:
            dic={}
            dic['numItem']=i
            if l.product_id and l.product_id.fe_tipo_item_id:
                dic['tipoItem']=int(l.product_id.fe_tipo_item_id.codigo)
            else:
                dic['tipoItem']=1
            dic['cantidad']=l.quantity_done
            dic['codigo']=l.product_id.default_code if l.product_id.default_code else 'NA'
            if l.product_uom.fe_unidad_id:
                dic['uniMedida']=int(l.product_uom.fe_unidad_id.codigo)
            else:
                dic['uniMedida']=59
            dic['numeroDocumento']=None
            dic['descripcion']=l.name
            dic['precioUni']=round(l.price_unit,6)
            dic['tributos']=None
            dic['ventaNoSuj']=0
            dic['ventaExenta']=0
            dic['ventaGravada']=0
            dic['codTributo']=None
            dic['montoDescu']= 0
            f.monto_total+=round(l.price_unit*l.quantity_done,6)

            #descuento=l.discount/100
            #valor_con_descuento=1-descuento
            
            #dic['montoDescu']=(l.price_unit*l.quantity*descuento)
            iva=False
            ivap=0
            exento=True
            nosujeto=False
            retencion=False
            persepcion=False
            isr=False
            tributos=[]
            
            
            lista.append(dic)
            i+=1
        return lista

    def get_resumen_nr(self):
        self.ensure_one()
        f=self
        resumen={}
        resumen['totalNoSuj']=0
        resumen['totalExenta']=0
        resumen['totalGravada']=0
        resumen['subTotalVentas']=0
        #total=resumen['subTotalVentas']+f.iva
        resumen['descuNoSuj']=0
        resumen['descuExenta']=0
        resumen['descuGravada']=0
        #resumen['descu']=0
        resumen['totalDescu']=0
        resumen['porcentajeDescuento']=0
        
        resumen['subTotal']=round(f.monto_total,2)
        #resumen['ivaPerci1']=round(f.percepcion,2)
        #resumen['ivaRete1']=round(f.retencion,2)
        #resumen['reteRenta']=round(abs(f.isr),2)
        resumen['montoTotalOperacion']=round(f.monto_total,2)
        #resumen['totalCompra']=round(f.nosujetas,2)
        #resumen['totalPagar']=round(resumen['totalCompra']-resumen['reteRenta'],2)
        resumen['totalLetras']=numero_to_letras(round(f.monto_total,2))
        ##resumen['totalIva']=round(f.iva,2)
        resumen['tributos']=None
        #resumen['observaciones']=f.observaciones
        #if f.invoice_payment_term_id.fe_condicion_id:
        #    resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        #else:
        #    resumen['condicionOperacion']=2
        return resumen







##-----------------------------------------------------------------------------------------------------------------------------------------------------------
##   COMUNES
##-----------------------------------------------------------------------------------------------------------------------------------------------------------        
    

    def get_emisor(self):
        self.ensure_one()
        f=self
        emisor={}
        emisor['nit']=f.company_id.partner_id.nit.replace('-','')
        emisor['nrc']=f.company_id.partner_id.nrc.replace('-','')
        emisor['nombre']=f.company_id.partner_id.name
        emisor['codActividad']=f.company_id.partner_id.fe_actividad_id.codigo
        emisor['descActividad']=f.company_id.partner_id.fe_actividad_id.name
        emisor['nombreComercial']=None
        emisor['tipoEstablecimiento']=f.company_id.fe_establecimiento_id.codigo
        emisor['direccion']=f.get_direccion(f.company_id.partner_id)
        emisor['telefono']=f.company_id.partner_id.phone
        emisor['correo']=f.company_id.partner_id.email
        emisor['codEstableMH']=None
        emisor['codEstable']=None
        emisor['codPuntoVentaMH']=None
        emisor['codPuntoVenta']=None
        
        return emisor
    
    def get_direccion(self,partner):
        self.ensure_one()
        f=self
        direccion={}
        direccion['departamento']=partner.fe_municipio_id.departamento_id.code
        direccion['municipio']=partner.fe_municipio_id.codigo
        direccion['complemento']=partner.street
        return direccion




    
    

    def get_pagos(self):
        return None

    def get_extension(self):
        self.ensure_one()
        f=self
        extension={}
        if f.entrega:
            extension['nombEntrega']=f.entrega
        if f.doc_entrega:
            extension['docuEntrega']=f.doc_entrega
        if f.recibe:
            extension['nombRecibe']=f.recibe
        if f.doc_recibe:
            extension['docuRecibe']=f.doc_recibe
        if f.observaciones:
            extension['observaciones']=f.observaciones
        if f.placa:
            extension['placaVehiculo']=f.placa
        if len(extension)==0:
            return None
        else:
            return extension
    

