import base64
import os
from datetime import date, datetime, timedelta

import xlsxwriter

# Libreria para ruta temporal
import tempfile

from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class PlanillaReport(models.TransientModel):
	_name = 'planilla.lomed.report'
	_inherit = 'hr.payslip.run'
		
	# BRANCH
	def print_planillas_report(self):
		# Get Report Data
		report_data = []

		# Prepare Excel Report
		report_file_name = self.prepare_excel_planilla_report(report_data)
		
		# Create Attachment
		attachment = self.create_attachment(report_file_name)

		return {
			'type': 'ir.actions.act_url',
			'url': '/web/content/%s?download=true' % attachment.id,
			'target': 'download',
		}

			
	# BRANCH EXCEL ---- aqui definimos las celdas que se van a crear en la hoja de excel
	def prepare_excel_planilla_report(self, report_data):
		name_base = 'Reporte de planilla.xlsx'
		file_name = tempfile.gettempdir() + '/' + name_base
		
		workbook = xlsxwriter.Workbook(file_name)
		worksheet = workbook.add_worksheet(name="Planilla")

		empresa = self.env.user.company_id.name

	# Aquí Definimos los formatos, para aplicar a las secciones que vayamos creando en excel 
		text_format = workbook.add_format({'align': 'center', 'valign': 'center', 'text_wrap': True,
										   'font_name': 'Calibri', 'font_size': '10', 'border': 1})
										   
		fecha = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'center', 'border': 1})
		mes_format = workbook.add_format({'num_format': 'mmmm', 'align': 'center', 'border': 1})
		
		text_format_1 = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'center', 'text_wrap': True,
											 'font_name': 'Calibri', 'font_size': '10', 'border': 1})
		column_titles_grey = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'center', 'text_wrap': True,
												  'font_name': 'Calibri', 'font_size': '10', 'border': 1,
												  'bg_color': '#D9D9D9'})
		column_titles_blue = workbook.add_format({'align': 'center', 'valign': 'center', 'text_wrap': True,
												  'font_name': 'Calibri', 'font_size': '10', 'border': 1,
												  'bg_color': '#BDD7EE'})
		column_titles_green = workbook.add_format({'align': 'center', 'valign': 'center', 'text_wrap': True,
												   'font_name': 'Calibri', 'font_size': '10', 'border': 1,
												   'bg_color': '#C4D79B'})
		column_titles_purple = workbook.add_format({'align': 'center', 'valign': 'center', 'text_wrap': True,
													'font_name': 'Calibri', 'font_size': '10', 'border': 1,
													'bg_color': '#ADB9CA'})
		column_titles_blue_1 = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'center', 'text_wrap': True,
													'font_name': 'Calibri', 'font_size': '10', 'border': 1, 'bg_color': '#BDD7EE'})
		column_titles_green_1 = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'center', 'text_wrap': True,
													 'font_name': 'Calibri', 'font_size': '10', 'border': 1,
													 'bg_color': '#C4D79B'})
		column_titles_purple_1 = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'center', 'text_wrap': True,
													 'font_name': 'Calibri', 'font_size': '10', 'border': 1,
													 'bg_color': '#ADB9CA'})
		column_titles_yellow_1 = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'center', 'text_wrap': True,
													 'font_name': 'Calibri', 'font_size': '10', 'border': 1})
													 
		currency_format = workbook.add_format({'align': 'center', 'valign': 'center', 'text_wrap': True,
											 'font_name': 'Calibri', 'font_size': '10', 'border': 1, 'num_format': '$#,##0.00'})
		currency_format_l = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'center', 'text_wrap': True,
											 'font_name': 'Calibri', 'font_size': '10', 'border': 1, 'num_format': '$#,##0.00'})





#########Aqui definimos las columnas que vamos a usar en la hoja 1 #########

		worksheet.set_landscape()
		worksheet.fit_to_pages(1, 0)
		worksheet.set_zoom(100)
		worksheet.set_row(0, 40)
		worksheet.set_column(0, 0, 15) #A
		worksheet.set_column(1, 1, 15) #B
		worksheet.set_column(2, 2, 20) #C
		worksheet.set_column(3, 3, 20) #D
		worksheet.set_column(4, 4, 20) #E
		worksheet.set_column(5, 5, 20) #F


		# Aquí empezamos a preparar los datos a mostrar (se crean las columnas según los datos que existan)
		row = 3
		column = 0
		
		worksheet.write(row, column, 'COD', column_titles_grey)

		
		#aquí definimos las cabeceras del excel 
		worksheet.write(row, column + 1, 'NOMBRE EMPLEADO', column_titles_grey)
		worksheet.write(row, column + 2, 'CUENTA', column_titles_grey)
		worksheet.write(row, column + 3, 'PAGO', column_titles_grey)
		worksheet.write(row, column + 4, 'SUELDO', column_titles_grey)
		worksheet.write(row, column + 5, 'DIAS EFECTIVOS', column_titles_grey)
		worksheet.write(row, column + 6, 'AFP/IPSFA', column_titles_grey)
		worksheet.write(row, column + 7, 'SALARIO', column_titles_grey)
		worksheet.write(row, column + 8, 'VACACION', column_titles_grey)
		worksheet.write(row, column + 9, 'BONOS', column_titles_grey)
		worksheet.write(row, column + 10, 'HRS EXTRA', column_titles_grey)
		worksheet.write(row, column + 11, 'COMISIONES', column_titles_grey)
		worksheet.write(row, column + 12, 'TOTAL', column_titles_grey)
		worksheet.write(row, column + 13, 'AFP', column_titles_grey)
		worksheet.write(row, column + 14, 'ISSS', column_titles_grey)
		worksheet.write(row, column + 15, 'IPSFA', column_titles_grey)
		worksheet.write(row, column + 16, 'SALARIO', column_titles_grey)
		worksheet.write(row, column + 17, 'ISR', column_titles_grey)
		worksheet.write(row, column + 18, 'PRESTAMOS BANCARIOS', column_titles_grey)
		worksheet.write(row, column + 19, 'FACTURAS', column_titles_grey)
		worksheet.write(row, column + 20, 'OTROS DESCUENTOS', column_titles_grey)
		worksheet.write(row, column + 21, 'DEPRECIACIONS Y OTRAS PRESTACIONES', column_titles_grey)
		worksheet.write(row, column + 22, 'LIQUIDO', column_titles_grey)
		worksheet.write(row, column + 23, 'CUENTA BANCARIA', column_titles_grey)

		for record in self:
			# Aquí 'record' es el registro actual de hr.payslip.run
			payslips = record.slip_ids
			start_date = record.date_start.strftime('%Y-%m-%d 00:00:01')
			end_date = record.date_end.strftime('%Y-%m-%d 23:59:59')
			inicio = record.date_start.strftime('%d-%m-%Y')
			fin = record.date_end.strftime('%d-%m-%Y')
			desde = 'Del: '
			hasta = ' Al: '
			periodo = desde + inicio + hasta + fin

			t_sueldo = 0.00
			t_vacacion = 0.00
			t_bonos_lomed = 0.00
			t_r_he = 0.00
			t_r_comis = 0.00
			t_afpl = 0.00
			t_isssl = 0.00
			t_IPSFAl = 0.00
			t_isr = 0.00
			t_bancos = 0.00
			t_od = 0.00
			t_oi = 0.00
			t_neto = 0.00

			row = 0
			column = 0

			#recorremos el lote de recibos de nomina que se va exportar
			for payslip in payslips:
				empleado = payslip.employee_id
				contrato = empleado.contract_id

				codigo_empleado = empleado.barcode
				nombre_empleado = empleado.name
				sueldo = contrato.wage
				afp_empleado = empleado.afp
				cuenta_empleado = empleado.cuenta

				worksheet.write(row + 1, column + 1, codigo_empleado or '', text_format)
				worksheet.write(row + 1, column + 2, nombre_empleado or '', text_format)
				worksheet.write(row + 1, column + 3, '' or '', text_format)
				worksheet.write(row + 1, column + 4, 'QUINCENAL' or '', text_format)
				worksheet.write(row + 1, column + 5, sueldo or '', currency_format)
				worksheet.write(row + 1, column + 6, '' or '', text_format)
				worksheet.write(row + 1, column + 7, afp_empleado or '', text_format)

				lineas = payslip.line

				for linea in lineas:
					categoria = linea.category_id.code
					regla = linea.salary_rule_id.code
					amount = linea.amount

					if categoria == 'sueldo':
						worksheet.write(row + 1, column + 8, amount or '', currency_format)
						t_sueldo += amount
					elif categoria == 'vacacion':
						worksheet.write(row + 1, column + 9, amount or '', currency_format)
						t_vacacion += amount
					elif categoria == 'bonos_lomed':
						worksheet.write(row + 1, column + 10, amount or '', currency_format)
						t_bonos_lomed += amount
					elif regla == 'r_he':
						worksheet.write(row + 1, column + 11, amount or '', currency_format)
						t_r_he += amount
					elif categoria == 'r_comis':
						worksheet.write(row + 1, column + 12, amount or '', currency_format)
						t_r_comis += amount
					elif categoria == 'afpl':
						worksheet.write(row + 1, column + 14, amount or '', currency_format)
						t_afpl += amount
					elif categoria == 'isssl':
						worksheet.write(row + 1, column + 15, amount or '', currency_format)
						t_isssl += amount
					elif categoria == 'IPSFAl':
						worksheet.write(row + 1, column + 16, amount or '', currency_format)
						t_IPSFAl += amount
					elif categoria == 'isr':
						worksheet.write(row + 1, column + 17, amount or '', currency_format)
						t_isr += amount
					elif categoria == 'bancos':
						worksheet.write(row + 1, column + 19, amount or '', currency_format)
						t_bancos += amount
					elif categoria == 'od':
						worksheet.write(row + 1, column + 20, amount or '', currency_format)
						t_od += amount
					elif categoria == 'oi':
						worksheet.write(row + 1, column + 21, amount or '', currency_format)
						t_oi += amount
					elif categoria == 'neto':
						worksheet.write(row + 1, column + 22, amount or '', currency_format)
						t_neto += amount


				worksheet.write(row + 1, column + 23, cuenta_empleado or '', text_format)

				row += 1
				
			#aqui establecemos las sumas de los datos

			worksheet.write(row + 1, column + 8, t_sueldo or '', currency_format)

			worksheet.write(row + 1, column + 9, t_vacacion or '', currency_format)

			worksheet.write(row + 1, column + 10, t_bonos_lomed or '', currency_format)

			worksheet.write(row + 1, column + 11, t_r_he or '', currency_format)

			worksheet.write(row + 1, column + 12, t_r_comis or '', currency_format)

			worksheet.write(row + 1, column + 14, t_afpl or '', currency_format)

			worksheet.write(row + 1, column + 15, t_isssl or '', currency_format)

			worksheet.write(row + 1, column + 16, t_IPSFAl or '', currency_format)

			worksheet.write(row + 1, column + 17, t_isr or '', currency_format)

			worksheet.write(row + 1, column + 19, t_bancos or '', currency_format)

			worksheet.write(row + 1, column + 20, t_od or '', currency_format)

			worksheet.write(row + 1, column + 21, t_oi or '', currency_format)

			worksheet.write(row + 1, column + 22, t_neto or '', currency_format)

			#worksheet.write(row, column, '', text_format)

			# Escribimos
			worksheet.merge_range(0, 0, 0, 5, empresa, currency_format_l)
			worksheet.merge_range(1, 0, 1, 5, 'Planilla lomed', currency_format_l)
			worksheet.merge_range(2, 0, 2, 5, periodo, currency_format_l)

			workbook.close()
			return file_name


	def create_attachment(self, file_name):
		ir_attachment_obj = self.env['ir.attachment']

		# Read File data
		with open(file_name, "rb+") as file:
			file_data = base64.encodebytes(file.read())
			file.close()

		# Remove tmp file
		os.remove(file_name)

		# Delete Old Attachment
		attachments = ir_attachment_obj.search([('name', '=', 'Planilla lomed.xlsx'),
												('res_model', '=', 'hr.payslip.run')])
		attachments and attachments.unlink()

		return ir_attachment_obj.create({
			'name': 'Planilla lomed.xlsx',
			'datas': file_data,
			'store_fname': 'Planilla lomed.xlsx',
			'res_model': 'hr.payslip.run',
			'type': 'binary'
		})



