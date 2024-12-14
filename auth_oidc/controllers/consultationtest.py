from odoo.http import request
import json
from odoo import http
from odoo.exceptions import ValidationError, AccessDenied

import logging
_logger = logging.getLogger(__name__)

class ConsultationTest(http.Controller):
    
    @http.route("/consulta/prueba" , auth="public", type="json")