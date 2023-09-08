# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.onchange('pricelist_id')
	def _compute_unit_price_with_pricelist(self):
		for order in self:
			for line in order.order_line:
				if line.product_id and order.pricelist_id:
					pricelist_id = order.pricelist_id
					new_list_price = pricelist_id._get_product_price(line.product_id, line.product_uom_qty)
					if new_list_price != 0.0:
						final_price = new_list_price
					else:
						final_price = line.product_id.with_company(order.company_id).lst_price
					line.write({
						'price_unit' : final_price,
						'discount': 0.0
					})


	def _prepare_invoice(self):
		res = super(SaleOrder, self)._prepare_invoice()
		if res:
			res.update({
				'pricelist_id': self.pricelist_id.id,
				'currency_id' : self.pricelist_id.currency_id.id
			})
		return res


class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"
	_description = "Sales Order Line"


	@api.depends('product_id')
	def _compute_product_uom(self):
		for line in self:
			if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
				line.product_uom = line.product_id.uom_id
			line.order_id._compute_unit_price_with_pricelist()

	@api.depends('product_id', 'product_uom', 'product_uom_qty')
	def _compute_price_unit(self):
		for line in self:
			# check if there is already invoiced amount. if so, the price shouldn't change as it might have been
			# manually edited
			line.order_id._compute_unit_price_with_pricelist()
			if line.qty_invoiced > 0:
				continue
			if not line.product_uom or not line.product_id or not line.order_id.pricelist_id:
				line.price_unit = 0.0
			else:
				price = line.with_company(line.company_id)._get_display_price()
				line.price_unit = line.product_id._get_tax_included_unit_price(
					line.company_id,
					line.order_id.currency_id,
					line.order_id.date_order,
					'sale',
					fiscal_position=line.order_id.fiscal_position_id,
					product_price_unit=price,
					product_currency=line.currency_id
				)
