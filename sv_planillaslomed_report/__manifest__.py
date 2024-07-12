{
	#  Information
	'name': 'Planillas report Lomed',
	'version': '16.0',
	'summary': '',
	'price': 150.0,
	'description': 'Reporte de planillas para Lomed SA DE CV',
	'category': '',

	# Author
	'author': 'Josué Henríquez by Aron asesores',
	'website': 'https://www.aronasesores.com',
	'license': '',

	#  Depends
	'depends': ['hr_payroll', 'hr', 'hr_attendance', 'hr_contract', 'hr_expense', 'sv_rrhh'],
	'external_dependencies': {},
	'data': [
		'views/planillas_report_view.xml',
		'security/ir.model.access.csv'

	],
	
	

	#  Others
	'installable': True,
	'auto_install': False,

}
