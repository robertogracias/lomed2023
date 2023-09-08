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
from datetime import datetime
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
    numero_letras = numero_letras+" CON " + str(decimal) +"/100"
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

class sv_fe_move(models.Model):
    _inherit='account.move'
    uuid=fields.Char("Codigo de Generacion",copy=False)
    sello=fields.Char("Sello",copy=False)
    control=fields.Char("Numero de control",copy=False)

    date_confirm=fields.Datetime('Fecha de confirmacion',copy=False)

    gravadas=fields.Float("Ventas Gravadas")
    exentas=fields.Float("Ventas Exentas")
    nosujetas=fields.Float("Ventas No Sujetas")
    gravadas_des=fields.Float("Descuento Gravado ")
    exentas_des=fields.Float("Descuento Exento")
    nosujetas_des=fields.Float("Descuento Exento")
    retencion=fields.Float("Retencion")
    percepcion=fields.Float("Percepcion")
    isr=fields.Float("ISR")
    iva=fields.Float("IVA")
    entrega=fields.Char("Entrega",copy=False)
    doc_entrega=fields.Char("Doc. Entrega",copy=False)
    recibe=fields.Char("Recibe",copy=False)
    doc_recibe=fields.Char("Doc. Recibe",copy=False)
    observaciones=fields.Char("Observacione",copy=False)
    placa=fields.Char("Placa Vehiculo",copy=False)

    doc_json=fields.Text("Doc JSON",copy=False)
    doc_firmado=fields.Text("Doc. Firmado",copy=False)
    doc_sellado=fields.Text("Doc. Sellado",copy=False)
    doc_respuesta=fields.Text("Respuesta",copy=False)




    def generar_fe(self):
        self.ensure_one()
        f=self
        
        #generando el dte
        #dte=str(f.get_factura())
        #dte=dte.replace('None','null')
        #dte=dte.replace('False','null')
        #dte=dte.replace('\'','\"')
        #firmandolo
        firma={}
        firma['nit']=f.company_id.partner_id.nit.replace('-','')
        firma['passwordPri']=f.company_id.fe_ambiente_id.llave_privada
        if f.tipo_documento_id.codigo=='Factura':
            firma['dteJson']=f.get_factura()
        elif f.tipo_documento_id.codigo=='CCF':
            firma['dteJson']=f.get_ccf()
        else:
            return
        f.doc_json=firma['dteJson']
        encabezado = {"content-type": "application/JSON","User-Agent":"Odoo/16"}
        json_datos = json.dumps(firma)
        json_datos=json_datos.replace('None','null')
        json_datos=json_datos.replace('False','null')
        #raise UserError(json_datos)
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
            result=requests.post(f.company_id.fe_ambiente_id.url+'/fesv/recepciondte',data=json_datos, headers=encabezado)
            f.doc_respuesta=result.text
            respuesta=json.loads(result.text)
            if respuesta['estado']=='PROCESADO':
                f.sello=respuesta['selloRecibido']
            #raise UserError(result.text)
        #raise UserError(result.text)

    def get_factura(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_fac()
        dic['documentoRelacionado']=None
        dic['emisor']=f.get_emisor()
        dic['receptor']=f.get_receptor()
        dic['otrosDocumentos']=f.get_otros()
        dic['ventaTercero']=f.get_terceros()
        dic['cuerpoDocumento']=f.get_cuerpo()
        dic['resumen']=f.get_resumen()
        dic['extension']=f.get_extension()
        dic['apendice']=None
        return dic

    def get_ccf(self):
        self.ensure_one()
        f=self
        dic={}
        dic['identificacion']=f.get_identificacion_fac()
        dic['documentoRelacionado']=None
        dic['emisor']=f.get_emisor()
        dic['receptor']=f.get_receptor()
        dic['otrosDocumentos']=f.get_otros()
        dic['ventaTercero']=f.get_terceros()
        dic['cuerpoDocumento']=f.get_cuerpo()
        dic['resumen']=f.get_resumen()
        dic['extension']=f.get_extension()
        dic['apendice']=None
        return dic
    
    def get_identificacion_fac(self):        
        self.ensure_one()
        f=self
        if not f.uuid:
            f.uuid=str(uuid.uuid4()).upper()
        identificacion={}
        identificacion['version']=f.tipo_documento_id.version
        identificacion['ambiente']=f.company_id.fe_ambiente_id.codigo
        identificacion['tipoDte']=f.tipo_documento_id.fe_tipo_doc_id.codigo
        identificacion['numeroControl']='DTE-'+f.tipo_documento_id.fe_tipo_doc_id.codigo.zfill(2)+'-00000000-'+str(f.id).rjust(15,'0')
        f.control=identificacion['numeroControl']
        identificacion['codigoGeneracion']=f.uuid
        identificacion['tipoModelo']=1
        identificacion['tipoOperacion']=1
        identificacion['tipoContingencia']=None
        identificacion['motivoContin']=None
        identificacion['fecEmi']=f.invoice_date.strftime('%Y-%m-%d')
        identificacion['horEmi']=f.invoice_date.strftime('%H:%M:%S')
        identificacion['tipoMoneda']='USD'        
        return identificacion
    
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
        direccion['departamento']=partner.state_id.code
        direccion['municipio']=partner.fe_municipio_id.codigo
        direccion['complemento']=partner.street
        return direccion
        
    def get_receptor(self):
        self.ensure_one()
        f=self
        if f.partner_id.nit!="NA":
            receptor={}
            receptor['nit']=f.partner_id.nit.replace('-','')
            receptor['nrc']=f.partner_id.nrc.replace('-','')
            receptor['nombre']=f.partner_id.name
            receptor['codActividad']=f.partner_id.fe_actividad_id.codigo
            receptor['descActividad']=f.partner_id.fe_actividad_id.name
            receptor['nombreComercial']=None
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

    def get_cuerpo_fac(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=0
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
            dic['numeroDocumento']=None
            dic['cantidad']=l.quantity
            dic['codigo']=l.product_id.default_code
            dic['codTributo']=None
            if l.product_uom_id.fe_unidad_id:
                dic['uniMedida']=int(l.product_uom_id.fe_unidad_id.codigo)
            else:
                dic['uniMedida']=59
            dic['descripcion']=l.name
            dic['precioUni']=l.price_unit
            dic['montoDescu']=(l.price_unit*l.quantity*l.discount)
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
                ivap=t.amount/100
                exento=True if t.tax_group_id.code=='exento' else False
                nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                retencion=True if t.tax_group_id.code=='retencion' else False
                persepcion=True if t.tax_group_id.code=='persepcion' else False
                isr=True if t.tax_group_id.code=='isr' else False
                f.retencion+=((l.price_unit*l.quantity*l.discount)*(t.amount/100)) if t.tax_group_id.code=='retencion' else 0
                f.percepcion+=((l.price_unit*l.quantity*l.discount)*(t.amount/100)) if t.tax_group_id.code=='persepcion' else 0
                f.isr+=((l.price_unit*l.quantity*l.discount)*(t.amount/100)) if t.tax_group_id.code=='isr' else 0
                if t.fe_tributo_id:
                    if  t.fe_tributo_id.codigo!='20':
                        tributos.append(t.fe_tributo_id.codigo)
            if iva:
                dic['ventaNoSuj']=0
                dic['ventaExenta']=0
                dic['ventaGravada']=round((l.price_unit*l.quantity*(1-(l.discount/100)))*(1+ivap),2)
                dic['precioUni']=round(l.price_unit*(1+ivap),2)
                f.gravadas_des+=(l.price_unit*l.quantity*l.discount)
            elif exento:
                dic['ventaNoSuj']=0
                dic['ventaExenta']=round((l.price_unit*l.quantity**(1-(l.discount/100))),2)
                dic['ventaGravada']=0
                f.exentas_des+=(l.price_unit*l.quantity*l.discount)
            elif nosujeto:
                dic['ventaNoSuj']=round((l.price_unit*l.quantity**(1-(l.discount/100))),2)
                dic['ventaExenta']=0
                dic['ventaGravada']=0
                f.nosujetas_des+=(l.price_unit*l.quantity*l.discount)
            f.gravadas+=dic['ventaGravada']
            f.exentas+=dic['ventaExenta']
            f.nosujetas+=dic['ventaNoSuj']
            if len(tributos)>0:
                dic['tributos']=tributos
            else:
                dic['tributos']=None
            dic['psv']=0
            dic['noGravado']=0
            dic['ivaItem']=round((l.price_unit*l.quantity**(1-(l.discount/100)))*(ivap),2)
            f.iva+=dic['ivaItem']
            lista.append(dic)
            i+=1
        return lista
    
    def get_cuerpo_ccf(self):
        self.ensure_one()
        f=self
        f.gravadas=0
        f.exentas=0
        f.nosujetas=0
        f.gravadas_des=0
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
            dic['numeroDocumento']=None
            dic['cantidad']=l.quantity
            dic['codigo']=l.product_id.default_code
            dic['codTributo']=None
            if l.product_uom_id.fe_unidad_id:
                dic['uniMedida']=int(l.product_uom_id.fe_unidad_id.codigo)
            else:
                dic['uniMedida']=59
            dic['descripcion']=l.name
            dic['precioUni']=l.price_unit
            dic['montoDescu']=(l.price_unit*l.quantity*l.discount)
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
                ivap=t.amount/100
                exento=True if t.tax_group_id.code=='exento' else False
                nosujeto=True if t.tax_group_id.code=='nosujeto' else False
                retencion=True if t.tax_group_id.code=='retencion' else False
                persepcion=True if t.tax_group_id.code=='persepcion' else False
                isr=True if t.tax_group_id.code=='isr' else False
                f.retencion+=((l.price_unit*l.quantity*l.discount)*(t.amount/100)) if t.tax_group_id.code=='retencion' else 0
                f.percepcion+=((l.price_unit*l.quantity*l.discount)*(t.amount/100)) if t.tax_group_id.code=='persepcion' else 0
                f.isr+=((l.price_unit*l.quantity*l.discount)*(t.amount/100)) if t.tax_group_id.code=='isr' else 0
                if t.fe_tributo_id:
                    tributos.append(t.fe_tributo_id.codigo)
            if iva:
                dic['ventaNoSuj']=0
                dic['ventaExenta']=0
                dic['ventaGravada']=round((l.price_unit*l.quantity*(1-(l.discount/100)))*(1+ivap),2)
                dic['precioUni']=round(l.price_unit*(1+ivap),2)
                f.gravadas_des+=(l.price_unit*l.quantity*l.discount)
            elif exento:
                dic['ventaNoSuj']=0
                dic['ventaExenta']=round((l.price_unit*l.quantity**(1-(l.discount/100))),2)
                dic['ventaGravada']=0
                f.exentas_des+=(l.price_unit*l.quantity*l.discount)
            elif nosujeto:
                dic['ventaNoSuj']=round((l.price_unit*l.quantity**(1-(l.discount/100))),2)
                dic['ventaExenta']=0
                dic['ventaGravada']=0
                f.nosujetas_des+=(l.price_unit*l.quantity*l.discount)
            f.gravadas+=dic['ventaGravada']
            f.exentas+=dic['ventaExenta']
            f.nosujetas+=dic['ventaNoSuj']
            if len(tributos)>0:
                dic['tributos']=tributos
            else:
                dic['tributos']=None
            dic['psv']=0
            dic['noGravado']=0
            #dic['ivaItem']=round((l.price_unit*l.quantity**(1-(l.discount/100)))*(ivap),2)
            f.iva+=(round((l.price_unit*l.quantity**(1-(l.discount/100)))*(ivap),2))
            lista.append(dic)
            i+=1
        return lista

    def get_resumen(self):
        self.ensure_one()
        f=self
        if f.tipo_documento_id.codigo=='Factura':
            return f.get_resumen_fac()
        elif f.tipo_documento_id.codigo=='CCF':
            return f.get_resumen_ccf()
        else:
            return None

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
        resumen['montoTotalOperacion']=round(resumen['subTotal']-resumen['ivaRete1']-resumen['reteRenta'],2)
        resumen['totalNoGravado']=0
        resumen['totalPagar']=round(resumen['montoTotalOperacion'],2)
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

    def get_resumen_ccf(self):
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
        if len(tributos)>0:
            resumen['tributos']=tributos
        else:
            resumen['tributos']=None
        resumen['subTotal']=round(resumen['subTotalVentas']-resumen['totalDescu'],2)
        resumen['ivaPerci1']=round(f.percepcion,2)
        resumen['ivaRete1']=round(f.retencion,2)
        resumen['reteRenta']=round(f.isr,2)
        resumen['montoTotalOperacion']=round(resumen['subTotal']-resumen['ivaRete1']-resumen['reteRenta'],2)
        resumen['totalNoGravado']=0
        resumen['totalPagar']=round(resumen['montoTotalOperacion'],2)
        resumen['totalLetras']=numero_to_letras(round(resumen['totalPagar'],2))
        ##resumen['totalIva']=round(f.iva,2)
        resumen['saldoFavor']=0
        if f.invoice_payment_term_id.fe_condicion_id:
            resumen['condicionOperacion']=int(f.invoice_payment_term_id.fe_condicion_id.codigo)
        else:
            resumen['condicionOperacion']=2
        resumen['pagos']=f.get_pagos()
        resumen['numPagoElectronico']=None
        return resumen
    

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
    



