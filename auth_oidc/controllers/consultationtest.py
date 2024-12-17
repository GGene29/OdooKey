from odoo.http import request
import json
from odoo import http
from odoo.exceptions import ValidationError, AccessDenied

import logging
_logger = logging.getLogger(__name__)

class ConsultationTest(http.Controller):
    
    @http.route("/practica" , auth="public", type="http", methods=['GET'],website=True)
    def practique_log(self, **post):
        _logger.info('====================')
        _logger.info('\n\n')
        _logger.info('CONSULTA')
        return "CONSULTA DE PRUEBA"