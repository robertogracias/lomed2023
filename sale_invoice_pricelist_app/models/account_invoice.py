# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from contextlib import ExitStack, contextmanager


class AccountMoveUpdate(models.Model):
	_inherit = 'account.move'

	pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True, states={'draft': [('readonly', False)]}, help="Pricelist for current account invoice.")
	check_pricelist = fields.Boolean(compute="_compute_unit_price_with_pricelist",string="Check Priclist")

	@api.depends('pricelist_id','invoice_line_ids','line_ids')
	def _compute_unit_price_with_pricelist(self):
		for order in self:
			container = {'records': self, 'self': self}
			for line in order.with_context(check_move_validity=False,skip_account_move_synchronization=True).invoice_line_ids:
				if line.product_id:
					final_price=None
					if line.move_id.move_type in ('out_invoice', 'out_refund'):
						pricelist_id = order.pricelist_id
						for l in pricelist_id:
							final_price = l._get_product_price(line.product_id, line.quantity)
					else:
						final_price = line._compute_price_unit()
					line.with_context(check_move_validity=False,skip_account_move_synchronization=True).update({
						'price_unit' : final_price,
					})
			account_debit = sum([line.debit for line in order.line_ids])
			account_credit = sum([line.credit for line in order.line_ids])
			if order.move_type == 'out_invoice':
				account_debit_line_ids = self.env['account.move.line'].search([('id','in',order.line_ids.ids),('debit','!=', 0.0)], limit=1)
				account_debit_line_ids.update({'debit': account_credit})
			else:
				account_credit_line_ids = self.env['account.move.line'].search([('id','in',order.line_ids.ids),('credit','!=', 0.0)], limit=1)
				account_credit_line_ids.update({'credit': account_debit})
			order.with_context(check_move_validity=False,skip_account_move_synchronization=True).update({'check_pricelist': True})

	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			partner = self.env['res.partner'].browse(vals.get('partner_id'))
			vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
		invoice = super(AccountMoveUpdate, self).create(vals_list)
		return invoice

	@api.onchange('partner_id')
	def _onchange_partner_id(self):
		result = super(AccountMoveUpdate, self)._onchange_partner_id()
		if self.move_type in ('out_invoice', 'out_refund'):
			if self.partner_id:
				self.pricelist_id = self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False
		return result
