# -*- coding: utf-8 -*-
# from odoo import http
import logging
import pprint
import werkzeug
import json
import requests

from odoo import http
from odoo.http import request
from werkzeug.utils import redirect


_logger = logging.getLogger(__name__)

class test_agrosania(http.Controller):
    
    @http.route('/jasper', auth='user')
    def get_test(self, **kw):
        response = redirect("https://report.multicongelados.net/jasperserver/flow.html?_flowId=viewReportFlow&standAlone=true&j_acegi_security_check?&j_username=congelados&j_password=mc2020&userLocale=es_SV&_flowId=viewReportFlow&ParentFolderUri=/sv/reportes/impuestos&reportUnit=/sv/reportes/impuestos/VentasContribuyente&decorate=no&userTimezone=Etc/UTC")
        return response

    