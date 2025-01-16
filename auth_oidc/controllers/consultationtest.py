from odoo.http import request
import json
from odoo import http
from odoo.exceptions import ValidationError, AccessDenied
from odoo import models, fields, api, _
from odoo import SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

class ConsultationTest(http.Controller):
    
    """ Estructura para recibir informacion por axios desde express
    El type del decorador debe ser JSON, de lo contrario dara un error
    El cors se usa en algunos casos que Axios presenta problemas
    """
    @http.route("/practica" , auth="public", type="json", methods=['POST'],website=True, cors='*', csrf=False)
    def practique_log(self, **post):
        usuarios = request.env['res.users'].sudo().search([()])
        
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
    
    #Asignacion de grupos al usuario de odoo en funcion de los roles de KC
    def kc_roles_tests(self,validation):
        #Roles del usuario, extraidos del user-info de KC
        kc_user_roles = validation['groups']
        #Roles de KC
        _logger.info('-------------------Roles de KC-------------------')
        _logger.info(kc_user_roles)
        #Consultamos el usuario de odoo
        odoo_user = request.env['res.users'].sudo().search([('login','=',validation['email'])], limit=1)
        _logger.info('Prueba de roles de KC ---Grupos antes de agregar los nuevos grupos---')
        _logger.info(odoo_user.groups_id)
        #En esta parte se consulta el grupo que se va a agregar al usuario
        if odoo_user:
            #Iteramos los roles que contiene el user-info de KC
            for role in kc_user_roles:
                #Segun el rol asignamos grupos
                if role == 'test-roles-admin' and odoo_user.user_has_groups('!base.group_user,!base.group_no_one,!mail.group_mail_template_editor'):
                    groups_test_odoo = request.env.ref('base.group_user').id,request.env.ref('base.group_no_one').id,request.env.ref('mail.group_mail_template_editor').id,
                    _logger.info('Prueba de roles de KC ---Se agregara el grupo de usuario interno---')
                    break
                elif role == 'test-roles-portal' and odoo_user.user_has_groups('!base.group_portal'):
                    _logger.info('-------------------------------------')
                    groups_test_odoo = request.env.ref('base.group_portal').id,
                    _logger.info('Prueba de roles de KC ---Se agrego el grupo de usuario portal---')
                    break
                #Si no tienen ningun rol que amerite agregar algun grupo
                else:
                    groups_test_odoo = False
                    
            groups_list = list(groups_test_odoo)
            #Se agregan los grupos al usuario 
            #Agregando los grupos al usuario el ".with_user(SUPERUSER_ID)" evita el error de singleton.
            odoo_user.with_user(SUPERUSER_ID).sudo().write({'groups_id': [(6,0, groups_list)]})
            _logger.info('Prueba de roles de KC ---Agrega los nuevos grupos---')
            _logger.info(odoo_user.groups_id)