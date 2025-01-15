from odoo.http import request
import json
from odoo import http
from odoo.exceptions import ValidationError, AccessDenied
from odoo import models, fields, api, _

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
        #Datos del usuario, en este caso solo usaremos los roles
        kc_user_roles = validation['groups']
        #Roles de KC
        _logger.info('Prueba de roles de KC -------------------')
        _logger.info(kc_user_roles)
        _logger.info('Prueba de roles de KC -------------------')
        #Consulta del usuario de odoo
        odoo_user = request.env['res.users'].sudo().search([('login','=',validation['email'])])
        _logger.info('Prueba de roles de KC ---ID del usuario de odoo---')
        _logger.info(odoo_user)
        _logger.info('Prueba de roles de KC ---ID del usuario de odoo---')
        _logger.info('Prueba de roles de KC ---Grupos antes de agregar nuevos grupos---')
        _logger.info(odoo_user.groups_id)
        _logger.info('Prueba de roles de KC ---Grupos antes de agregar nuevos grupos---')

        #Diccionario que contiene los ids de los grupos que se van a agregar al usuario
        if odoo_user:
            #En esta parte se consulta el grupo que se va a agregar al usuario
            #Iteramos los roles que contiene el user-info de KC
            for role in kc_user_roles:
                #Segun el rol asignamos grupos
                if role == 'test-roles-admin':
                    groups_test_odoo = (self.env['res.groups'].browse(['base.group_user']).ids,)
                    _logger.info('Prueba de roles de KC ---Se agrego el grupo de usuario interno---')
                if role == 'test-roles-portal':
                    groups_test_odoo = (self.env['res.groups'].browse(['base.group_portal']).ids,)
                    _logger.info('Prueba de roles de KC ---Se agrego el grupo de usuario portal---')
            _logger.info('Prueba de roles de KC ---Grupo para Agregar---')
            _logger.info(groups_test_odoo)
            _logger.info(type(groups_test_odoo))
            _logger.info('Prueba de roles de KC ---Grupo para Agregar---')
            #Se verifica que los grupos a agregar no esten ya presentes en el usuario de odoo
            verif_groups_exists = self.groups_verif(odoo_user,groups_test_odoo)
            #Se agregan los grupos al usuario 
            if groups_test_odoo and verif_groups_exists:
                odoo_user.sudo().write({'groups_id': [(5, )]})
                _logger.info('Prueba de roles de KC -------------------')
                odoo_user.sudo().write({'groups_id': [(4, groups_test_odoo)]})
                _logger.info('Prueba de roles de KC -------------------')
            _logger.info('Prueba de roles de KC ---Grupos despues de agregar nuevos---')
            _logger.info(odoo_user.groups_id)
            _logger.info('Prueba de roles de KC ---Grupos despues de agregar nuevos---')
            
    def groups_verif(self, odoo_user,groups_to_add):
        #Itera los grupos del usuario de odoo
        for group_odoo in odoo_user.groups_id:
            if groups_to_add.index(group_odoo):
                return False
            else:
                return True