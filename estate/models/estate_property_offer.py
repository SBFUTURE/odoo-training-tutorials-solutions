from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'
    _order = 'price desc'

    price = fields.Float(string='Price')
    status = fields.Selection(
        string='Status',
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner', 
        required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    
    property_type_id = fields.Many2one(
        'estate.property.type',
        related='property_id.property_type_id',
        string='Property Type',
        store=True
    )

    validity = fields.Integer(string='Validity (days)', default=7, required=True)
    date_deadline = fields.Date(string="Deadline", compute='_compute_date_deadline', inverse='_inverse_date_deadline', store=True)

    _sql_constraints = [
        ('check_price_positive', 'CHECK(price >= 0)', 'The price must be positive.'),
    ]

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = datetime.now().date() + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                create_date = record.create_date.date() if record.create_date else datetime.now().date()
                record.validity = (record.date_deadline - create_date).days

    def action_accept(self):
        for record in self:
            if record.status == 'refused':
                raise UserError("You cannot accept a refused offer.")
            record.status = 'accepted'
            record.property_id.write({
                "selling_price": record.price,
                "buyer_id": record.partner_id.id,
                "status": 'offer_accepted'
            })
        return True

    def action_refuse(self):
        for record in self:
            if record.status == 'accepted':
                raise UserError("You cannot refuse an accepted offer.")
            record.status = 'refused'
        return True

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        for vals in vals_list:
            property_id = self.env['estate.property'].browse(vals.get('property_id'))
            if property_id.status != 'new':
                raise UserError("You cannot create an offer for a property that is not new.")
            
            existing_offers = self.search([('property_id', '=', vals['property_id'])])
            if existing_offers and any(offer.price >= vals['price'] for offer in existing_offers):
                raise UserError("You cannot create an offer with a lower amount than an existing offer.")
            
            property_id.status = 'offer_received'
        
        records = super(EstatePropertyOffer, self).create(vals_list)
        return records