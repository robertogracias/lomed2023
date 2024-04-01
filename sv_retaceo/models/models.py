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
    _inherit='stock.landed.cost'
    referencia=fields.Char("Referencia")
    declaracion=fields.Char("No. de Declaracion")
    comentario=fields.Text("Comentario")
    