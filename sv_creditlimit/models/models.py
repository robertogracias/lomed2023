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


class odoosv_partner(models.Model):
    _inherit='res.partner'
    credit_limit=fields.Float("Limite de Credito()")

    @api.constrains('credit_limit')
    def _check_credit(self):
        for r in self:
            if r.credit_limit>0:
                #obteniendo el credito actual del cliente
                debit_result=self.env['account.move.line'].read_group([('partner_id','=',r.id),('parent_state','=','posted'),('account_id','=',r.property_account_receivable_id.id)],['partner_id','debit'],['partner_id'])
                credit_result=self.env['account.move.line'].read_group([('partner_id','=',r.id),('parent_state','=','posted'),('account_id','=',r.property_account_receivable_id.id)],['partner_id','credit'],['partner_id'])
                if len(debit_result)>0:
                    debito=debit_result[0]['debit']
                    credito=credit_result[0]['credit']
                    if (debito-credito)>r.credit_limit:
                        raise ValidationError('El limite de credito se ha excedido')

class odoosv_invoice(models.Model):
    _inherit='account.move'

    @api.constrains('amount_total','partner_id')
    def _check_credit(self):
        for r in self:
            if r.move_type=='out_invoice':
                if r.partner_id.credit_limit>0:
                    #obteniendo el credito actual del cliente
                    debit_result=self.env['account.move.line'].read_group([('partner_id','=',r.partner_id.id),('move_id','!=',r.id),('parent_state','=','posted'),('account_id','=',r.partner_id.property_account_receivable_id.id)],['partner_id','debit'],['partner_id'])
                    credit_result=self.env['account.move.line'].read_group([('partner_id','=',r.partner_id.id),('move_id','!=',r.id),('parent_state','=','posted'),('account_id','=',r.partner_id.property_account_receivable_id.id)],['partner_id','credit'],['partner_id'])
                    if len(debit_result)>0:
                        debito=debit_result[0]['debit']
                        credito=credit_result[0]['credit']
                        if (debito+r.amount_total-credito)>r.partner_id.credit_limit:
                            raise ValidationError('El limite de credito se ha excedido: Credito Aprobado:'+str(r.partner_id.credit_limit)+' Credito requerido:'+str(debito+r.amount_total-credito))


                
class odoosv_aproval_category(models.Model):
    _inherit='approval.category'
    code=fields.Char("Codigo")

#class odoosv_aproval(models.Model):
#    _inherit='approval.request'
#    def action_approve(self):
#        res=super.action_approve()
#        for r in self:
#            if r.category_id.code=='credit_limit':
#                if r.request_owner_id.id==self.env.user.id:
#                    raise ValidationError('La solicitud no puede ser probada por el usuario que la presento')
#                if r.partner_id:
#                    r.partner_id.write({'credit_limit':r.amount})
#        return res


