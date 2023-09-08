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




class odoosv_canal_partner(models.Model):
    _inherit='res.partner'
    canal_id=fields.Many2one(comodel_name='odoosv.canal',string='Canal de venta')

class odoosv_canal_move(models.Model):
    _inherit='account.move'
    canal_id=fields.Many2one(comodel_name='odoosv.canal',string='Canal de venta',related='partner_id.canal_id',store=True)

class odoosv_canal_moveline(models.Model):
    _inherit='account.move.line'
    canal_id=fields.Many2one(comodel_name='odoosv.canal',string='Canal de venta',related='move_id.canal_id',store=True)

class odoosv_canal_saleorder(models.Model):
    _inherit='sale.order'
    canal_id=fields.Many2one(comodel_name='odoosv.canal',string='Canal de venta',related='partner_id.canal_id',store=True)

class odoosv_canal_saleorderline(models.Model):
    _inherit='sale.order.line'
    canal_id=fields.Many2one(comodel_name='odoosv.canal',string='Canal de venta',related='order_id.canal_id',store=True)

class odoosv_canal(models.Model):
    _name='odoosv.canal'
    _description='Canal de venta'
    name=fields.Char("Canal")

