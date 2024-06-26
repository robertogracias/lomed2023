from odoo.tools.translate import _
from odoo import api, fields, models, _


class AccountRevarsal(models.TransientModel):
	_inherit = 'account.move.reversal'

	def reverse_moves(self):
		moves = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_id
		if moves.move_type == 'out_invoice':
			default_values_list = []
			for move in moves:
				default_values_list.append({
					'ref': _('Reversal of: %s, %s') % (move.name, self.reason) if self.reason else _('Reversal of: %s') % (move.name),
					'date': self.date or move.date,
					'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
					'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
					'invoice_payment_term_id': None,
					'auto_post': True if self.date > fields.Date.context_today(self) else False,
				})
		else:
			default_values_list = []
			for move in moves:
				default_values_list.append({
					'ref': _('Reversal of: %s, %s') % (move.name, self.reason) if self.reason else _('Reversal of: %s') % (move.name),
					'date': self.date or move.date,
					'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
					'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
					'invoice_payment_term_id': None,
					'auto_post': True if self.date > fields.Date.context_today(self) else False,
				})
		if self.refund_method == 'cancel':
			if any([vals.get('auto_post', False) for vals in default_values_list]):
				new_moves = moves._reverse_moves(default_values_list)
			else:
				new_moves = moves._reverse_moves(default_values_list, cancel=True)
		elif self.refund_method == 'modify':
			moves._reverse_moves(default_values_list, cancel=True)
			moves_vals_list = []
			for move in moves.with_context(include_business_fields=True):
				moves_vals_list.append(move.copy_data({
					'date': self.date or move.date,
				})[0])
			new_moves = self.env['account.move'].create(moves_vals_list)
		elif self.refund_method == 'refund':
			new_moves = moves._reverse_moves(default_values_list)
		else:
			return

		action = {
			'name': _('Reverse Moves'),
			'type': 'ir.actions.act_window',
			'res_model': 'account.move',
		}
		if len(new_moves) == 1:
			action.update({
				'view_mode': 'form',
				'res_id': new_moves.id,
			})
		else:
			action.update({
				'view_mode': 'tree,form',
				'domain': [('id', 'in', new_moves.ids)],
			})
		return action
 