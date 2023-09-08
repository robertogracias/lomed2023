# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#
##############################################################################
import base64
from dataclasses import field
import json
import requests
import logging
import time
from markupsafe import Markup
from collections import defaultdict
from datetime import datetime
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools import float_compare, float_is_zero, plaintext2html
_logger = logging.getLogger(__name__)


class odoosv_empleado(models.Model):
    _inherit='hr.employee'
    #Datos generales
    nombre=fields.Char("Nombre")
    apellido=fields.Char("Primer Apellido")
    apellido2=fields.Char("Segundo Apellido")
    apellido_casada=fields.Char("Apellido de casada")
    dui=fields.Char("DUI")
    dui_lugar=fields.Char("Lugar de expedición del DUI")
    dui_fecha=fields.Date("Fecha de expedición del DUI")
    nit=fields.Char("NIT")
    profesion=fields.Char("Profesion/Officio")
    pasaporte=fields.Char("Pasaporte")
    nup=fields.Char("NUP")
    isss=fields.Char("ISSS")
    afp=fields.Char("Nombre de la AFP")
    direccion=fields.Char("Direccion")
    domicilio=fields.Char("Domicilio")
    edad=fields.Char("Edad",compute='_get_edad')
    beneficiario_ids=fields.One2many(comodel_name='odoosv.empleado_beneficiario',inverse_name='empleado_id',string='Beneficiarios')
    prestamo_ids=fields.One2many(comodel_name='odoosv.empleado_prestamo',inverse_name='empleado_id',string='Prestamos')
    cuenta=fields.Char("Cuenta Bancaria")
    codigo=fields.Char("Codigo")
    pensionado = fields.Boolean(string="Es Pensionado", default=False)
    #Datos de empleo
    fecha_inicio=fields.Char("Fecha de inicio")
    fecha_retiro=fields.Char("Fecha de Retiro")
    

    @api.depends('birthday')
    def _get_edad(self):
        for r in self:
            edad=0
            if self.birthday:
                edad = (datetime.now().date() - self.birthday).days / 365.2425
                edad = int(edad)
                if int(edad) < 0:
                    edad=0
            r.edad=edad


class odoosv_mapcuentas(models.Model):
    _name='odoosv.hr.mapeo'
    name=fields.Char("Mapeo de cuentas")
    line_ids=fields.One2many(comodel_name='odoosv.hr.mapeo.line',inverse_name='mapeo_id',string="Mapeos")

class odoosv_mapcuentas_detail(models.Model):
    _name='odoosv.hr.mapeo.line'
    source_id=fields.Many2one('account.account',string="Cuenta Origen")
    target_id=fields.Many2one('account.account',string="Cuenta Destino")
    mapeo_id=fields.Many2one('odoosv.hr.mapeo',string="Mapeo")



class odoosv_contract(models.Model):
    _inherit='hr.contract'
    aplica_horas_extra=fields.Boolean("Aplicar horas extra")
    mapeo_id=fields.Many2one('odoosv.hr.mapeo',string="Mapeo")




class odoosv_beneficiario(models.Model):
    _name='odoosv.empleado_beneficiario'
    _description='Benficiarios de los empleados'
    name=fields.Char("Nombre")
    parentezco=fields.Char("Parentezco")
    fecha_nacimiento=fields.Date("Fecha de nacimiento")
    porcentaje=fields.Float("Porcentaje")
    empleado_id=fields.Many2one(comodel_name='hr.employee',string='Empleado')

    @api.constrains('porcentaje')
    def _check_restriciones(self):
        for l in self:
            if l.porcentaje<0:
                raise ValidationError('El porcentaje debe ser mayor que 0')


class odoosv_prestamo(models.Model):
    _name='odoosv.empleado_prestamo'
    _description='Prestamos de empleados'
    name=fields.Char("Referencia")
    financiera_id=fields.Many2one(comodel_name='odoosv.hr_financiera',string='Institucion')
    empleado_id=fields.Many2one(comodel_name='hr.employee',string='Empleado')
    monto=fields.Float("Monto")
    fecha_inicio=fields.Date("Fecha de inicio")
    fecha_fin=fields.Date("Fecha de última cuota")
    cuota_quincena1=fields.Float("Cuota primera Quincena")
    cuota_quincena2=fields.Float("Cuota segunda Quincena")



class odoosv_institucio(models.Model):
    _name='odoosv.hr_financiera'
    _description='Institucion financiera'
    name=fields.Char('Nombre de la institucion')
    codigo=fields.Char('Código para cálculos')
    categoria_id = fields.Many2one(
        string='Categoría',
        comodel_name='hr.salary.rule.category',
        ondelete='restrict',
    )
    
    estructura_id=fields.Many2one(comodel_name='hr.payroll.structure',string='Structura Salarial para genera regla')


    def crear_regla(self):
        for r in self:
            dic={}
            dic['name']=r.name
            dic['code']='r_'+r.codigo
            dic['active']=True
            dic['sequence']=260
            dic['appears_on_payslip']=True
            dic['condition_select']='python'
            dic['condition_python']="""
monto=0.0
for p in employee.prestamo_ids:
    if p.financiera_id.codigo=='"""+r.codigo+"""':
        if p.fecha_inicio<payslip.date_from:
            if p.fecha_fin>payslip.date_from:
                if payslip.payslip_run_id.quincena=='1':
                    monto=p.cuota_quincena1
                if payslip.payslip_run_id.quincena=='2':
                    monto=p.cuota_quincena2
result = (monto>0)
            """
            dic['amount_select']='code'
            dic['category_id']=r.categoria_id.id
            dic['struct_id']=r.estructura_id.id
            dic['amount_python_compute']="""
monto=0.0
for p in employee.prestamo_ids:
    if p.financiera_id.codigo=='"""+r.codigo+"""':
        if p.fecha_inicio<payslip.date_from:
            if p.fecha_fin>payslip.date_from:
                if payslip.payslip_run_id.quincena=='1':
                    monto=p.cuota_quincena1
                if payslip.payslip_run_id.quincena=='2':
                    monto=p.cuota_quincena2
result = round(monto*-1,2)
            """
            self.env['hr.salary.rule'].create(dic)



class odoosv_payslip(models.Model):
    _inherit='hr.payslip'
    horas_extra=fields.Float('Horas Extra')
    horas_extra_nocturna=fields.Float('Horas Extra Nocturnas')
    horas_asueto=fields.Float('Horas Asueto')
    dias_vacaciones=fields.Float('Dias de vacaciones')
    dias_incapacidad=fields.Float('Dias de incapacidad')
    otros_ingresos=fields.Float('Otros ingresos')
    otros_descuentos=fields.Float('Otros descuentos')

    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = defaultdict(lambda: defaultdict(lambda: self.env['hr.payslip']))
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip
        for journal_id in slip_mapped_data: # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]: # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += plaintext2html(slip.number or '' + ' - ' + slip.employee_id.name or '')
                    move_dict['narration'] += Markup('<br/>')
                    for line in slip.line_ids.filtered(lambda line: line.category_id):
                        amount = line.total
                        if line.code == 'NET': # Check if the line is the 'Net Salary'.
                            for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                                    if amount > 0:
                                        amount -= abs(tmp_line.total)
                                    elif amount < 0:
                                        amount += abs(tmp_line.total)
                        if float_is_zero(amount, precision_digits=precision):
                            continue
                        debit_account_id = line.salary_rule_id.account_debit.id
                        credit_account_id = line.salary_rule_id.account_credit.id
                        ###reemplazando las cuentas
                        if slip.contract_id and slip.contract_id.mapeo_id:
                            for c in slip.contract_id.mapeo_id.line_ids:
                                if debit_account_id:
                                    if c.source_id and c.source_id.id==debit_account_id:
                                        debit_account_id=c.target_id.id
                                if credit_account_id:
                                    if c.source_id and c.source_id.id==credit_account_id:
                                        credit_account_id=c.target_id.id

                        if debit_account_id: # If the rule has a debit account.
                            debit = amount if amount > 0.0 else 0.0
                            credit = -amount if amount < 0.0 else 0.0

                            debit_line = self._get_existing_lines(
                                line_ids, line, debit_account_id, debit, credit)

                            if not debit_line:
                                debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                                line_ids.append(debit_line)
                            else:
                                debit_line['debit'] += debit
                                debit_line['credit'] += credit

                        if credit_account_id: # If the rule has a credit account.
                            debit = -amount if amount < 0.0 else 0.0
                            credit = amount if amount > 0.0 else 0.0
                            credit_line = self._get_existing_lines(
                                line_ids, line, credit_account_id, debit, credit)

                            if not credit_line:
                                credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                                line_ids.append(credit_line)
                            else:
                                credit_line['debit'] += debit
                                credit_line['credit'] += credit

                for line_id in line_ids: # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                # The code below is called if there is an error in the balance between credit and debit sum.
                acc_id = slip.sudo().journal_id.default_account_id.id
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_credit = next(existing_adjustment_line, False)

                    if not adjust_credit:
                        adjust_credit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': 0.0,
                            'credit': debit_sum - credit_sum,
                        }
                        line_ids.append(adjust_credit)
                    else:
                        adjust_credit['credit'] = debit_sum - credit_sum

                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_debit = next(existing_adjustment_line, False)

                    if not adjust_debit:
                        adjust_debit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': credit_sum - debit_sum,
                            'credit': 0.0,
                        }
                        line_ids.append(adjust_debit)
                    else:
                        adjust_debit['debit'] = credit_sum - debit_sum

                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self.env['account.move'].sudo().create(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})
        return True


#    def _prepare_line_values(self, line, account_id, date, debit, credit):
#        res = super(odoosv_payslip, self)._prepare_line_values(line, account_id, date, debit, credit)
#        for r in res:
#            if r.contract_id and self.contract_id.mapeo_id:
#                for c in self.contract_id.mapeo_id.line_ids:
#                    if c.source_id and c.source_id.id==account_id:
#                        res['account_id']=c.target_id.id
#        return res



class odoosv_paysliprun(models.Model):
    _inherit='hr.payslip.run'
    estructura_id=fields.Many2one(comodel_name='hr.payroll.structure',string='Structura Salarial')
    fecha_calculo=fields.Date("Fecha de calculo")
    fecha_considerar=fields.Date("Fecha a considerar")
    comentario=fields.Text("Comentario")
    quincena=fields.Selection(selection=[('1', 'Quincena 1')
                                    ,('2', 'Quincena 2')
                                    ,('3', 'Otra')]
                                    , string='Quincena',default='1')
    #reporte_planilla=fields.Char("Reporte Planilla",compute='compute_reportes')
    #reporte_planilla_patronal=fields.Char("Reporte Planilla Patronal",compute='compute_reportes')
    #reporte_recibos=fields.Char("Reporte Recibos",compute='compute_reportes')

    def calcular(self):
        for r in self:
            for p in r.slip_ids:
                p.write({'struct_id':r.estructura_id})
                p.compute_sheet()

    def imprimir(self):
        x=1

    #def compute_reportes(self):
    #    for r in self:
    #        texto1=''
    #        texto2=''
    #        texto3=''
    #        jasper=r.company_id.jasper
    #        if not jasper:
    #            jasper=self.env['odoosv.jasper'].search([('name','=','odoo')],limit=1)
    #        if jasper:
    #            texto1=jasper.create_link_report('/sv/reportes/hr','Planilla',r.id,'')
    #            texto2=jasper.create_link_report('/sv/reportes/hr','PlanillaPatronal',r.id,'')
    #            texto3=jasper.create_link_report('/sv/reportes/hr','Recibos',r.id,'')
    #        r.reporte_planilla=texto1
    #        r.reporte_planilla_patronal=texto2
    #        r.reporte_recibos=texto3

#############


###planillas mensuales
class svrrhh_planillamensual(models.Model):
    _name='odoosv.planilla_mensual'
    _description='Planilla mensual'
    _inherit=['mail.thread']
    name=fields.Char(string='Planilla mensual')
    dias=fields.Integer(string='Dias')
    horas=fields.Integer(string='Horas')
    fecha=fields.Date(string='Fecha')
    comentario=fields.Text(string='Comentario')
    planillas=fields.Many2many(comodel_name='hr.payslip.run')
    empleado_ids=fields.One2many(comodel_name='odoosv.planilla_mensual.empleado',inverse_name='planilla_mensual_id',string='Empleados')

  


class svrrhh_planillamensualempleado(models.Model):
    _name='odoosv.planilla_mensual.empleado'
    _description='Planilla mensual por empleado'
    name=fields.Char('Registro')
    employee_id=fields.Many2one(comodel_name='hr.employee',string='Empleado')
    planilla_mensual_id=fields.Many2one(comodel_name='odoosv.planilla_mensual',string='Planilla Mensual')
    afp_laboral=fields.Float(string='AFP Laboral')
    afp_patronal=fields.Float(string='AFP Patronal')
    isss_laboral=fields.Float(string='ISSS Laboral')
    isss_patronal=fields.Float(string='ISSS Patronal')
    dias_trabajados=fields.Integer(string='Dias trabajados')
    dias_vacacion=fields.Integer(string='Dias vacacion')
    monto_vacacion=fields.Float(string='Monto vacacion')
    pago_adicional=fields.Float(string='Pago Adicional')
    salario=fields.Float(string='Salario')
    isr=fields.Float(string='Renta')
    comentario=fields.Char(string='Comentario')
    codigo_afp = fields.Char(string="Código AFP")
    horas = fields.Float(string="Horas")

class svrrhh_work_entry(models.Model):
    _inherit = ['hr.work.entry.type']
    incluir_en_salario = fields.Boolean(string='Incluir en salario',default=False)

class svrrhh_res_company(models.Model):
    _inherit = ['res.company']
    numeropatronal = fields.Char(string="Número Patronal ISSS")


    









    
    
    
    
    
    