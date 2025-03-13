from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'estate.property.type'
    _order = 'name asc'
    

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    sequence = fields.Integer('Sequence', default=10, help="Used to order property types")
    offer_ids = fields.One2many(
        'estate.property.offer', 
        'property_type_id',
        string='Offers',
    )
    offer_count = fields.Integer(
        string='Offer Count',
        compute='_compute_offer_count',
    )
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Property Type name already exists!'),
    ]

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)