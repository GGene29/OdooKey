# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api,_,tools
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from lxml import etree

from pymongo import MongoClient
import logging

_logger = logging.getLogger(__name__)

class OpStudentCourse(models.Model):
    _name = "op.student.course"
    _description = "Student Course Details"
    _inherit = "mail.thread"
    _rec_name = 'student_id'

    student_id = fields.Many2one('op.student', 'Student',
                                 ondelete="cascade", tracking=True)
    course_id = fields.Many2one('op.course', 'Course', required=True, tracking=True)
    batch_id = fields.Many2one('op.batch', 'Batch', tracking=True)
    roll_number = fields.Char('Roll Number', tracking=True)
    subject_ids = fields.Many2many('op.subject', string='Subjects')
    academic_years_id = fields.Many2one('op.academic.year', 'Academic Year')
    academic_term_id = fields.Many2one('op.academic.term', 'Terms')
    state = fields.Selection([('running', 'Running'),
                              ('finished', 'Finished')],
                             string="Status", default="running")

    _sql_constraints = [
        ('unique_name_roll_number_id',
         'unique(roll_number,course_id,batch_id,student_id)',
         'Roll Number & Student must be unique per Batch!'),
        ('unique_name_roll_number_course_id',
         'unique(roll_number,course_id,batch_id)',
         'Roll Number must be unique per Batch!'),
        ('unique_name_roll_number_student_id',
         'unique(student_id,course_id,batch_id)',
         'Student must be unique per Batch!'),
    ]

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Student Course Details'),
            'template': '/openeducat_core/static/xls/op_student_course.xls'
        }]


class OpStudent(models.Model):
    _name = "op.student"
    _description = "Student"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {"res.partner": "partner_id"}

    first_name = fields.Char('First Name',  translate=True)
    middle_name = fields.Char('Middle Name', translate=True)
    last_name = fields.Char('Last Name', translate=True)
    birth_date = fields.Date('Birth Date')
    blood_group = fields.Selection([
        ('A+', 'A+ve'),
        ('B+', 'B+ve'),
        ('O+', 'O+ve'),
        ('AB+', 'AB+ve'),
        ('A-', 'A-ve'),
        ('B-', 'B-ve'),
        ('O-', 'O-ve'),
        ('AB-', 'AB-ve')
    ], string='Blood Group')
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other')
    ], 'Gender', required=True, default='m')
    nationality = fields.Many2one('res.country', 'Nationality')
    emergency_contact = fields.Many2one('res.partner', 'Emergency Contact')
    visa_info = fields.Char('Visa Info', size=64)
    id_number = fields.Char('ID Card Number', size=64)
    partner_id = fields.Many2one('res.partner', 'Partner',
                                 required=True, ondelete="cascade")
    user_id = fields.Many2one('res.users', 'User', ondelete="cascade")
    gr_no = fields.Char("Registration Number", size=20)
    category_id = fields.Many2one('op.category', 'Category')
    course_detail_ids = fields.One2many('op.student.course', 'student_id',
                                        'Course Details',
                                        tracking=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [(
        'unique_gr_no',
        'unique(gr_no)',
        'Registration Number must be unique per student!'
    )]

    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        if not self.middle_name:
            self.name = str(self.first_name) + " " + str(
                self.last_name
            )
        else:
            self.name = str(self.first_name) + " " + str(
                self.middle_name) + " " + str(self.last_name)

    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than current date!"))

    @api.onchange('email')
    def _validate_email(self):
        if self.email and not tools.single_email_re.match(self.email):
            raise ValidationError(_('Invalid Email! Please enter a valid email address.'))
        

    @api.onchange("mobile")
    def _validate_mobile(self):
        if self.mobile and self.mobile.isalpha():
            raise ValidationError(_("Enter Your Valid Mobile Number"))

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Students'),
            'template': '/openeducat_core/static/xls/op_student.xls'
        }]

    def create_student_user(self):
        user_group = self.env.ref("base.group_portal") or False
        users_res = self.env['res.users']
        for record in self:
            if not record.user_id:
                user_id = users_res.create({
                    'name': record.name,
                    'partner_id': record.partner_id.id,
                    'login': record.email,
                    'groups_id': user_group,
                    'is_student': True,
                    'tz': self._context.get('tz'),
                })
                record.user_id = user_id
    

    @api.model
    def read(self, fields=None, load='_classic_read'):

        mongo_db = 'mongo_keycloak'
        mongo_collection = 'students'

        # Luego, busca los mismos registros en MongoDB
        try:
            client = MongoClient('mongodb://root:root@192.168.100.6:27017/')
        except Exception as e:
            _logger.info('**************************')
            _logger.warning(e)

        # Autenticación
        db = client[mongo_db]

        # Consulta a la colección
        collection = db[mongo_collection]
        mongo_records = collection.find()
        all_records = list(mongo_records) 

        _logger.info('---------------------------------')
        _logger.info(all_records)


        records = super(OpStudent, self).read(fields=fields, load=load)

        return records
    

    # @api.model
    # def write(self, vals):
    #     # Lógica personalizada antes de llamar al método original
    #     print("#################################################################")


    #     # Llamar al método original
    #     result = super(OpStudent, self).write(vals)

    #     # Aquí puedes agregar lógica para actualizar la base de datos externa (MongoDB)
    #     # self._update_mongo_db(vals)
    #     return result
    

    # def _update_mongo_db(self, vals):
    #     mongo_db = 'mongo_keycloak'
    #     mongo_collection = 'students'

    #     # Conectar a MongoDB
    #     try:
    #         client = MongoClient('mongodb://root:root@192.168.100.6:27017/')
    #         db = client[mongo_db]
    #         collection = db[mongo_collection]
    #     except Exception as e:
    #         _logger.warning("Error al conectar a MongoDB: %s", e)
    #         return

    #     # Actualizar o insertar el registro en MongoDB
    #     for record in self:
    #         mongo_record = {
    #             'first_name': record.first_name,
    #             'middle_name': record.middle_name,
    #             'last_name': record.last_name,
    #             'email': vals.get('email', record.email),
    #             'birth_date': record.birth_date,
    #             'blood_group': record.blood_group,
    #             'gender': record.gender,
    #             'nationality': record.nationality.id,
    #             'emergency_contact': record.emergency_contact.id,
    #             'visa_info': record.visa_info,
    #             'id_number': record.id_number,
    #             'gr_no': record.gr_no,
    #             'category_id': record.category_id.id,
    #             'active': record.active,
    #         }
    #         # Aquí puedes decidir si deseas actualizar o insertar
    #         collection.update_one({'gr_no': record.gr_no}, {'$set': mongo_record}, upsert=True)

    #     print("Datos actualizados en MongoDB")

