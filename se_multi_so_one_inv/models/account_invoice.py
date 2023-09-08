# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    # @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(sale_order_line, self)._prepare_invoice_line(qty)
        res['sale_order_line_id'] = self.id
        return res


class account_invoice_line(models.Model):
    _inherit = 'account.move.line'

    sale_order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', ondelete='set null', select=True, readonly=True)
    sale_order_id = fields.Many2one('sale.order', related='sale_order_line_id.order_id', string='SO#')

class account_invoice(models.Model):
    _inherit = 'account.move'

    multiple_sale_orders = fields.Boolean(string='Multi Sale Orders', default=False)
    sale_order_id = fields.Many2one('sale.order', string='Sale Orders')
    sale_origin = fields.Char('Sale Origin')

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        if self.multiple_sale_orders == True:
            self.invoice_line_ids = False
        return super(account_invoice, self)._onchange_partner_id()

    @api.onchange('sale_order_id')
    def _onchange_sale_orders(self):
        if not self.sale_order_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.sale_order_id.partner_id.id

        new_lines = self.env['account.move.line']
        for line in self.sale_order_id.order_line:
            if line in self.invoice_line_ids.mapped('sale_order_line_id'):
                continue
            qty = line.product_uom_qty - line.qty_invoiced
            taxes = line.tax_id
            invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
            
            account = line.product_id.property_account_income_id or line.product_id.categ_id.property_account_income_categ_id
            if not account:
                raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') % (line.product_id.name, line.product_id.id, line.product_id.categ_id.name))
    
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            if fpos:
                account = fpos.map_account(account)
            
            data = {
                'sale_order_id': line.order_id.id,
                'sale_order_line_id': line.id,
                'name': line.name,
                #'sequence': line.sequence,
                'sale_line_ids': [(6, 0, [line.id])],
                'product_uom_id': line.product_uom.id,
                'product_id': line.product_id.id or False,
                'account_id': account.id,
                'price_unit': line.order_id.currency_id.compute(line.price_unit, self.currency_id, round=False),
                'quantity': qty,
                'discount': line.discount,
                # 'analytic_account_id': line.order_id and line.order_id.analytic_account_id.id,
                'tax_ids': invoice_line_tax_ids.ids,
            }

            new_line = new_lines.new(data)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        # for one_line in self.invoice_line_ids:
        #     one_line._onchange_price_subtotal()

        self.sale_order_id = False
        sale_order_ids = self.invoice_line_ids.mapped('sale_order_id')
        if sale_order_ids:
            self.invoice_origin = ', '.join(sale_order_ids.mapped('name'))
        return {}
