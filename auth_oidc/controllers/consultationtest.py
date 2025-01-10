from odoo.http import request
import json
from odoo import http
from odoo.exceptions import ValidationError, AccessDenied

import logging
_logger = logging.getLogger(__name__)

class ConsultationTest(http.Controller):
    
    """ Estructura para recibir informacion por axios desde express
    El type del decorador debe ser JSON, de lo contrario dara un error
    El cors se usa en algunos casos que Axios presenta problemas
    """
    @http.route("/practica" , auth="public", type="json", methods=['POST'],website=True, cors='*', csrf=False)
    def practique_log(self, **post):
        usuarios = request.env['res.users'].sudo().search([])
        
        _logger.info('====================')
        _logger.info('\n\n')
        _logger.info('CONSULTA')
        _logger.info('CONSULTA')
        _logger.info(usuarios[0])
        _logger.info('CONSULTA')
        _logger.info('CONSULTA')
        
        
        primer_usuario = {
            'name': usuarios[1].name,
            'email' : usuarios[1].login,
            'oauth_uid': usuarios[1].oauth_uid,
            
        }
        """ Al devolver alguna informacion se debe usar json.dumps ya que es la respuesta esperada """
        return json.dumps({'user': primer_usuario})