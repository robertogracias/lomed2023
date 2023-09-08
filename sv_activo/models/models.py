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
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)




class odoosv_activo(models.Model):
    _inherit='account.asset'
    categoria_id=fields.Many2one(comodel_name='odoosv.asset.category',string='Categoria de Activos')
    modelo=fields.Char("Modelo")
    marca=fields.Char("Marca")
    matricula=fields.Char("Matricula")
    productivo=fields.Boolean("Productivo")
    codigo=fields.Char("Codigo")
    serie=fields.Char("Número de serie")



class odoosv_activo_categoria(models.Model):
    _name='odoosv.asset.category'
    _description='Categoria de Activos'
    name=fields.Char("Nombre")

