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
        odoo_user = request.env['res.users'].sudo().search([('login','=',validation['email'])], limit=1)

        #Diccionario que contiene los ids de los grupos que se van a agregar al usuario
        if odoo_user:
            #En esta parte se consulta el grupo que se va a agregar al usuario
            #Iteramos los roles que contiene el user-info de KC
            for role in kc_user_roles:
                #Segun el rol asignamos grupos
                if role == 'test-roles-admin':
                    groups_test_odoo = request.env.ref('base.group_user').id,
                    _logger.info('Prueba de roles de KC ---Se agregara el grupo de usuario interno---')
                    break
                elif role == 'test-roles-portal':
                    groups_test_odoo = request.env.ref('base.group_portal').id,
                    _logger.info('Prueba de roles de KC ---Se agrego el grupo de usuario portal---')
                    break
                #Si no tienen ningun rol que amerite agregar algun grupo
                else:
                    _logger.info('Prueba de roles de KC ---No hay Grupo para Agregar---')
                    groups_test_odoo = False
            
            _logger.info('Prueba de roles de KC ---Grupo para Agregar---')
            _logger.info(groups_test_odoo)
            _logger.info('Prueba de roles de KC ---Grupo para Agregar---')
            #Se verifica que los grupos a agregar no esten ya presentes en el usuario de odoo
            verif_groups_exists = False
            if groups_test_odoo:
                verif_groups_exists = self.groups_verif(odoo_user,groups_test_odoo)
                _logger.info('Prueba de roles de KC ---Verificacion de grupos---')
                _logger.info(verif_groups_exists)
            #Se agregan los grupos al usuario 
            groups_list = list(groups_test_odoo)
            #Agregando el usuario a los grupos
            if verif_groups_exists:
                _logger.info(groups_list)
                #Agregando los grupos al usuario
                #odoo_user.sudo().write({'groups_id': [(6,0, groups_list)]})
                #Agregando el usuario a los grupos
                portal_group = request.env['res.groups'].sudo().browse(10)
                user_group = request.env['res.groups'].sudo().browse(1)
                portal_group.write({'users': [(3, odoo_user.id)]})
                user_group.write({'users': [(4, odoo_user.id)]})
                _logger.info('Prueba de roles de KC ---Agrega los nuevos grupos---')
            _logger.info('Prueba de roles de KC ---Grupos despues de agregar nuevos---')
            _logger.info(odoo_user.groups_id)
            _logger.info('Prueba de roles de KC ---Grupos despues de agregar nuevos---')
            
    def groups_verif(self, odoo_user,groups_to_add):
        _logger.info('Prueba de roles de KC ---Entra a la funcion de verif---')
        #Itera los grupos del usuario de odoo
        _logger.info(odoo_user.groups_id)
        for group_odoo in odoo_user.groups_id:
            _logger.info('Prueba de roles de KC ---Iteracion---')
            #Iteramos los grupos que vamos a agregar y los comparamos con los grupos agregados en el odoo
            for group in groups_to_add:
                #En caso de tener ya el grupo retorna False
                if group == group_odoo.id:
                    return False
            #Si no contiene los grupos a agregar retorna True
            return True