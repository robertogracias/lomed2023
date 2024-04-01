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


class sv_fe_company(models.Model):
    _inherit='res.company'
    fe_ambiente_id=fields.Many2one(comodel_name='sv_fe.ambiente',string='Ambiente')
    fe_modelo_facturacion_id=fields.Many2one(comodel_name='sv_fe.modelo',string='Modelo de facturacion')
    fe_transmision_id=fields.Many2one(comodel_name='sv_fe.transmision',string='Modelo de Transmision')
    fe_contingencia_id=fields.Many2one(comodel_name='sv_fe.contingencia',string='Tipo de contingencia')
    fe_establecimiento_id=fields.Many2one(comodel_name='sv_fe.tipo_establecimiento',string='Tipo de establecimiento')
    

class sv_fe_country(models.Model):
    _inherit='res.country'
    fe_codigo=fields.Char("Codigo")
    

    


class sv_fe_documento(models.Model):
    _inherit='odoosv.fiscal.document'
    fe_tipo_doc_id=fields.Many2one(comodel_name='sv_fe.tipo_doc',string="Tipo de documento")
    fe_generacion_id=fields.Many2one(comodel_name='sv_fe.generacion',string="Tipo de Generación del Documento")
    fe_doc_asociado_id=fields.Many2one(comodel_name='sv_fe.docasociado',string="Documento Asociado")
    fe_contingencia_id=fields.Many2one(comodel_name='sv_fe.doc_contingencia',string="Documento en contingencia")
    sequencia_id=fields.Many2one(comodel_name='ir.sequence',string="Numeracion")
    version=fields.Integer("Version")

class sv_fe_tax(models.Model):
    _inherit='account.tax'
    fe_retencion_id=fields.Many2one(comodel_name='sv_fe.retencion',string="Retención IVA MH")
    fe_tributo_id=fields.Many2one(comodel_name='sv_fe.tributo',string="Tributo")

class sv_fe_producto(models.Model):
    _inherit='product.template'
    fe_tipo_item_id=fields.Many2one(comodel_name='sv_fe.tipo_item',string="Tipo de ítem")



class sv_fe_partner(models.Model):
    _inherit='res.partner'
    fe_municipio_id=fields.Many2one(comodel_name='sv_fe.municipio',string="Municipio")
    fe_actividad_id=fields.Many2one(comodel_name='sv_fe.actividad',string="Actividad")
    fe_identificacion_id=fields.Many2one(comodel_name='sv_fe.doc_identificacion',string="Documento de identificacion")
    fe_tipo_persona_id=fields.Many2one(comodel_name='sv_fe.tipo_persona',string="Tipo de Persona")
    fe_domicilio_id=fields.Many2one(comodel_name='sv_fe.domicilio',string="Domicilio")
    comercial=fields.Char("Nombre Comercial")

class sv_fe_uom(models.Model):
    _inherit='uom.uom'
    fe_unidad_id=fields.Many2one(comodel_name='sv_fe.unidad',string="Unidad")


class sv_fe_condicion(models.Model):
    _inherit='account.payment.term'
    fe_condicion_id=fields.Many2one(comodel_name='sv_fe.condicion',string="Condicion")

class sv_fe_journal(models.Model):
    _inherit='account.journal'
    fe_formapago_ids=fields.Many2one(comodel_name='sv_fe.formapago',string="Formas de pago")


class sv_ve_incoterms(models.Model):
    _inherit='account.incoterms'
    fe_incoterm_id=fields.Many2one(comodel_name='sv_fe.incoterms',string="Incoterms")