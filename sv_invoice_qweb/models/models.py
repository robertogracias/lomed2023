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
#from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID
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



class odoosv_account_move(models.Model):
    _inherit='account.move'
    amount_letras=fields.Char("Monto en Letras",compute='get_monto_en_letras')

    gravado=fields.Float("gravado",compute='get_gravado')
    excento=fields.Float("Exento",compute='get_exento')
    nosujeto=fields.Float("No Sujeto",compute='get_nosujeto')
    iva=fields.Float("Iva",compute='get_iva')
    retenido=fields.Float("Retenido",compute='get_retenido')

    @api.depends('invoice_line_ids','amount_total')
    def get_gravado(self):
        for r in self:
            total=0.0
            for l in r.invoice_line_ids:
                gravado=False
                for t in l.tax_ids:
                    if t.tax_group_id.code=='iva':
                        gravado=True
                if gravado==True:
                    total+=l.price_subtotal
            r.gravado=total
    
    @api.depends('invoice_line_ids','amount_total')
    def get_exento(self):
        for r in self:
            total=0.0
            for l in r.invoice_line_ids:
                exento=False
                for t in l.tax_ids:
                    if t.tax_group_id.code=='exento':
                        exento=True
                if exento==True:
                    total+=l.price_subtotal
            r.excento=total
    
    @api.depends('invoice_line_ids','amount_total')
    def get_nosujeto(self):
        for r in self:
            total=0.0
            for l in r.invoice_line_ids:
                nosujeto=False
                for t in l.tax_ids:
                    if t.tax_group_id.code=='nosujeto':
                        nosujeto=True
                if nosujeto==True:
                    total+=l.price_subtotal
            r.nosujeto=total

    @api.depends('invoice_line_ids','amount_total')
    def get_iva(self):
        for r in self:
            total=0.0
            for l in r.line_ids:
                iva=False
                if l.display_type=='tax': 
                    if l.tax_line_id:
                        if l.tax_line_id.tax_group_id.code=='iva':
                            iva=True
                if iva==True:
                    total+=(l.credit-l.debit)
            r.iva=total

    @api.depends('invoice_line_ids','amount_total')
    def get_retenido(self):
        for r in self:
            total=0.0
            for l in r.line_ids:
                retenido=False
                if l.display_type=='tax':      
                    if l.tax_line_id:
                        if l.tax_line_id.tax_group_id.code=='retenido':
                            retenido=True
                if retenido==True:
                    total+=(l.credit-l.debit)
            r.retenido=total
    @api.depends('amount_total','x_version')
    def get_monto_en_letras(self):
        for r in self:
            if r.currency_id:
                r.amount_letras = numero_to_letras(r.amount_total)
            else:
                r.amount_letras = False

        



    
    

    

