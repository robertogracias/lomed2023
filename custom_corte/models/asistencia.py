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
from datetime import datetime, date
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta,date

class odoosv_asistencia(models.Model):
    _name = 'odoosv.asistencia'

    name=fields.Char("Asistencia",related='employee_id.name')
    employee_id=fields.Many2one(comodel_name='hr.employee',string='Empleado')
    department_id=fields.Many2one(comodel_name='hr.department',string='Area')
    fecha=fields.Date("Fecha")

    he_entrada=fields.Float("Hora de entrada esperada")
    he_salida_almuerzo=fields.Float("Hora de salida de almuerzo esperada")
    he_entrada_almuerzo=fields.Float("Hora de entrada de almuerzo esperada")
    he_salida=fields.Float("Hora de salida esperada")

    entrada=fields.Datetime("Hora de entrada")
    salida_almuerzo=fields.Datetime("Hora de salida de almuerzo")
    entrada_almuerzo=fields.Datetime("Hora de entrada de almuerzo")
    salida=fields.Datetime("Hora de salida")

    entrada_tarde=fields.Float("Entrada tarde de jornada")
    entrada_tarde_almuerzo=fields.Float("Entrada tarde de almuerzo")





    def procesar_fecha(self,fecha):
        #borrando los actuales
        self.env['odoosv.asistencia'].search([('fecha','=',fecha)]).unlink()
        inicio=datetime(fecha.year,fecha.month,fecha.day,0,0,1)
        fin=datetime(fecha.year,fecha.month,fecha.day,23,59,59)
        empleados=self.env['user.attendance'].search([('timestamp','>=',inicio),('timestamp','<=',fin)]).mapped('employee_id')
        for e in empleados:
            #asignando los datos del 
            dic={}
            dic['employee_id']=e.id
            dic['department_id']=e.department_id.id
            dic['fecha']=fecha
            #calculando los datos actuales
            contrato=e.contract_id
            if contrato and contrato.resource_calendar_id:
                dia=fecha.weekday()
                tiempo1=None
                tiempo2=None
                for d in contrato.resource_calendar_id.attendance_ids:
                    if str(dia)==d.dayofweek:
                        if not tiempo1:
                            tiempo1=d
                        else:
                            tiempo2=d
                if tiempo1 and tiempo2:
                    dic['he_entrada']=tiempo1.hour_from
                    dic['he_salida_almuerzo']=tiempo1.hour_to
                    dic['he_entrada_almuerzo']=tiempo2.hour_from
                    dic['he_salida']=tiempo2.hour_to
                elif tiempo1 and not tiempo2:
                    dic['he_entrada']=tiempo1.hour_from
                    dic['he_salida']=tiempo1.hour_to
            #calculando los datos de ingreso
            lst=self.env['user.attendance'].search([('timestamp','>=',inicio),('timestamp','<=',fin),('employee_id','=',e.id)],order="timestamp asc")
            if len(lst)==1:
                dic['entrada']=lst[0].timestamp
            elif len(lst)==2:
                dic['entrada']=lst[0].timestamp
                dic['salida']=lst[1].timestamp
            elif len(lst)==3:
                dic['entrada']=lst[0].timestamp
                dic['salida_almuerzo']=lst[1].timestamp
                dic['salida']=lst[2].timestamp
            elif len(lst)==4:
                dic['entrada']=lst[0].timestamp
                dic['salida_almuerzo']=lst[1].timestamp
                dic['entrada_almuerzo']=lst[2].timestamp
                dic['salida']=lst[3].timestamp
            elif len(lst)>4:
                dic['entrada']=lst[0].timestamp
                dic['salida_almuerzo']=lst[1].timestamp
                dic['entrada_almuerzo']=lst[2].timestamp
                dic['salida']=lst[3].timestamp
            self.env['odoosv.asistencia'].create(dic)




    def procesar_hoy(self):
        hoy=datetime.now().date()
        self.procesar_fecha(hoy)
    
    def procesar_mes(self):
        mes=datetime.now().date().month
        inicio=datetime(datetime.now().date().year,mes,1)
        running_date=inicio
        while running_date.month==mes:
            #raise ValidationError(str(running_date))
            self.procesar_fecha(running_date)
            running_date=running_date+timedelta(days=1)
    
    def procesar_mes_anterior(self):
        mes=datetime.now().date().month-1
        year=datetime.now().date().year
        if mes==0:
            mes=12
            year=year-1
        inicio=datetime(year,mes,1)
        running_date=inicio
        while running_date.month==mes:
            self.procesar_fecha(running_date)
            running_date=running_date+timedelta(days=1)
    
    








    


