
from odoo.tools.translate import _
from odoo import api, fields, models, _


class AccountConfig(models.TransientModel):
	_inherit = "res.config.settings"


	create_move_from_invoice = fields.Boolean('Create Stock Move From Invoice',related="company_id.create_move_from_invoice",readonly=False)
	
	warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse",related="company_id.warehouse_id",readonly=False)

	create_move_picking = fields.Selection(related="company_id.create_move_picking",
		string="Create Stock Move From Picking",readonly=False)


	def get_values(self):
		res = super(AccountConfig, self).get_values()
		create_move_from_invoice = self.env['ir.config_parameter'].sudo().get_param('bi_picking_move_from_invoice.create_move_from_invoice')
		create_move_picking= self.env['ir.config_parameter'].sudo().get_param('bi_picking_move_from_invoice.create_move_picking')
		warehouse_id = self.env['ir.config_parameter'].sudo().get_param('bi_picking_move_from_invoice.warehouse_id')
		vals = {}
		if create_move_from_invoice:
			vals['create_move_from_invoice'] = create_move_from_invoice
		if create_move_picking:
			vals['create_move_picking'] = create_move_picking
		if warehouse_id:
			vals['warehouse_id'] = int(warehouse_id)
		if vals:
			res.update(vals)

		return res

		return res
	def set_values(self):
		super(AccountConfig, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('bi_picking_move_from_invoice.create_move_from_invoice', self.create_move_from_invoice)
		self.env['ir.config_parameter'].sudo().set_param('bi_picking_move_from_invoice.create_move_picking', self.create_move_picking) 
		self.env['ir.config_parameter'].sudo().set_param('bi_picking_move_from_invoice.warehouse_id', self.warehouse_id.id) 
