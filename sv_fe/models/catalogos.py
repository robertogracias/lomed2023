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


class sv_fe_ambiente(models.Model):
    _name='sv_fe.ambiente'
    _description='Ambientes de facturacion electronica'
    name=fields.Char("Ambiente")
    codigo=fields.Char("Codigo")
    url=fields.Char("URL")

    token=fields.Text("token")
    token_vencimiento=fields.Datetime("Vencimiento")
    user=fields.Char("Usuario")
    password=fields.Char("Password")
    firmador=fields.Char("Firmador")
    llave_privada=fields.Char("Llave privada")

    def get_token(self):
        self.ensure_one()
        fecha=datetime.now()
        renovar=False
        if not self.token:
            renovar=True
        elif not self.token_vencimiento:
            renovar=True
        elif self.token_vencimiento<fecha:
            renovar=True
        if renovar==True:
            encabezado = {"content-type": "application/x-www-form-urlencoded","User-Agent":"Odoo/16"}
            dic={"user":self.user,"pwd":self.password}
            #raise UserError(self.url+'/seguridad/auth?'+dic)
            result = requests.post(self.url+'/seguridad/auth',params=dic, headers=encabezado)
            respuesta=json.loads(result.text)
            token=respuesta['body']['token']
            ##raise UserError(str(respuesta))
            self.token=token
            return token
        else:
            return self.token



class sv_fe_tipodoc(models.Model):
    _name='sv_fe.tipo_doc'
    _description='Tipo de documento'
    name=fields.Char("Tipo documento")
    codigo=fields.Char("Codigo")


class sv_fe_modelo(models.Model):
    _name='sv_fe.modelo'
    _description='Modelo de facturacion'
    name=fields.Char("Modelo de facturacion")
    codigo=fields.Char("Codigo")


class sv_fe_transmision(models.Model):
    _name='sv_fe.transmision'
    _description='Tipo de transmision'
    name=fields.Char("Tipo de transmision")
    codigo=fields.Char("Codigo")


class sv_fe_contingencia(models.Model):
    _name='sv_fe.contingencia'
    _description='Tipo de contingencia'
    name=fields.Char("Tipo de contingencia")
    codigo=fields.Char("Codigo")


class sv_fe_retencion(models.Model):
    _name='sv_fe.retencion'
    _description='Retención IVA MH'
    name=fields.Char("Retención IVA MH")
    codigo=fields.Char("Codigo")


class sv_fe_generacion(models.Model):
    _name='sv_fe.generacion'
    _description='Tipo de Generación del Documento'
    name=fields.Char("Tipo de Generación del Documento")
    codigo=fields.Char("Codigo")


class sv_fe_establecimiento(models.Model):
    _name='sv_fe.tipo_establecimiento'
    _description='Tipo de establecimiento'
    name=fields.Char("Tipo de establecimiento")
    codigo=fields.Char("Codigo")

class sv_fe_serviciomedico(models.Model):
    _name='sv_fe.servicio_medico'
    _description='Código tipo de Servicio (Médico)'
    name=fields.Char("Código tipo de Servicio (Médico)")
    codigo=fields.Char("Codigo")

class sv_fe_tipo_item(models.Model):
    _name='sv_fe.tipo_item'
    _description='Tipo de ítem'
    name=fields.Char("Tipo de ítem")
    codigo=fields.Char("Codigo")

class sv_fe_municipio(models.Model):
    _name='sv_fe.municipio'
    _description='Municipio'
    name=fields.Char("Municipio")
    codigo=fields.Char("Codigo")
    departamento_id=fields.Many2one(comodel_name='res.country.state',string='Departamento')


class sv_fe_unidad(models.Model):
    _name='sv_fe.unidad'
    _description='Unidad'
    name=fields.Char("Unidad")
    codigo=fields.Char("Codigo")

class sv_fe_tributo(models.Model):
    _name='sv_fe.tributo'
    _description='Tributo'
    name=fields.Char("Tributo")
    codigo=fields.Char("Codigo")

class sv_fe_condicion(models.Model):
    _name='sv_fe.condicion'
    _description='condicion'
    name=fields.Char("condicion")
    codigo=fields.Char("Codigo")

class sv_fe_formapago(models.Model):
    _name='sv_fe.formapago'
    _description='Forma pago'
    name=fields.Char("Forma de pago")
    codigo=fields.Char("Codigo")


class sv_fe_plazo(models.Model):
    _name='sv_fe.plazo'
    _description='Plazo'
    name=fields.Char("Plazo")
    codigo=fields.Char("Codigo")


class sv_fe_actividadeconomica(models.Model):
    _name='sv_fe.actividad'
    _description='Actividad economica'
    name=fields.Char("Actividad")
    codigo=fields.Char("Codigo")


class sv_fe_docasociado(models.Model):
    _name='sv_fe.docasociado'
    _description='Documento Asociado'
    name=fields.Char("Documento Asociado")
    codigo=fields.Char("Codigo")



class sv_fe_doc_identificacion(models.Model):
    _name='sv_fe.doc_identificacion'
    _description='Documento de identificacion'
    name=fields.Char("Documento indentificacion")
    codigo=fields.Char("Codigo")


class sv_fe_doc_contingencia(models.Model):
    _name='sv_fe.doc_contingencia'
    _description='Documento en contingencia'
    name=fields.Char("Documento en contingencia")
    codigo=fields.Char("Codigo")


class sv_fe_validacion(models.Model):
    _name='sv_fe.validacion'
    _description='Tipo de validacion'
    name=fields.Char("Tipo de validacion")
    codigo=fields.Char("Codigo")


class sv_fe_remision(models.Model):
    _name='sv_fe.remision'
    _description='Título a que se remiten los bienes'
    name=fields.Char("Título a que se remiten los bienes")
    codigo=fields.Char("Codigo")    

class sv_fe_donacion(models.Model):
    _name='sv_fe.donacion'
    _description='Tipo de Donación'
    name=fields.Char("Tipo de Donación")
    codigo=fields.Char("Codigo")   


class sv_fe_resinto(models.Model):
    _name='sv_fe.resinto'
    _description='Recinto fiscal'
    name=fields.Char("Recinto fiscal")
    codigo=fields.Char("Codigo")    



class sv_fe_regiment(models.Model):
    _name='sv_fe.regimen'
    _description='Regimen'
    name=fields.Char("Recinto fiscal")
    codigo=fields.Char("Codigo")    


class sv_fe_persona(models.Model):
    _name='sv_fe.tipo_persona'
    _description='Persona'
    name=fields.Char("Tipo de Persona")
    codigo=fields.Char("Codigo")    


class sv_fe_transporte(models.Model):
    _name='sv_fe.transporte'
    _description='Transporte'
    name=fields.Char("Ttransporte")
    codigo=fields.Char("Codigo")    


class sv_fe_incoterms(models.Model):
    _name='sv_fe.incoterms'
    _description='Incoterms'
    name=fields.Char("Incoterms")
    codigo=fields.Char("Codigo")    


class sv_fe_domicilio(models.Model):
    _name='sv_fe.domicilio'
    _description='Domicilio'
    name=fields.Char("Domicilio")
    codigo=fields.Char("Codigo")  