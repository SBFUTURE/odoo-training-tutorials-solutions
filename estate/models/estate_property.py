from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char(string='Title', required=True, default="Unknown")
    description = fields.Text()
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    zipcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string="Available from", default=lambda self: datetime.now() + timedelta(days=90), copy=False)
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2, string="Bedrooms")
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help='Garden Orientation'
    )
    active = fields.Boolean(default=True)
    status = fields.Selection(
        string='Status',
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        copy=False,
        default='new',
        required=True
    )
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user, copy=False)
    property_tag_ids = fields.Many2many('estate.property.tag', string='Property Tags')
    property_offers_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')

    total_area = fields.Integer(string="Total Area (sqm)", compute='_compute_total_area', store=True)
    best_offer = fields.Float(string="Best Price", compute='_compute_best_offer', store=True)

    _sql_constraints = [
        ('expected_price_positive', 'CHECK(expected_price >= 0)', 'The expected price must be positive.'),
        ('selling_price_positive', 'CHECK(selling_price >=0)', 'The selling price must be positive.'),
    ]
    @api.ondelete(at_uninstall=False)
    def _check_state_before_delete(self):
        for record in self:
            if record.status not in ['new', 'canceled']:
                raise UserError('You cannot delete a property that is not new or canceled.')

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends('property_offers_ids.price')
    def _compute_best_offer(self):
        for rec in self:
            rec.best_offer = rec.property_offers_ids and max(rec.property_offers_ids.mapped('price')) or 0.0
            

    @api.onchange('garden')
    def _onchange_garden(self):
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = False
        else:
            self.garden_area = 10
            self.garden_orientation = 'north'

    def action_cancel(self):
        for record in self:
            if record.status == 'sold':
                raise UserError('You cannot cancel a sold property.')
            record.status = 'canceled'
        return True

    def action_sold(self):
        for record in self:
            if record.status == 'canceled':
                raise UserError('You cannot sell a canceled property.')
            record.status = 'sold'
        return True

    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, precision_rounding=0.01) and float_compare(record.selling_price, record.expected_price * 0.9, precision_rounding=0.01) < 0:
                raise ValidationError('The selling price cannot be lower than 90% of the expected price.')

    @api.onchange('expected_price', 'selling_price')
    def _onchange_price_limited_validation(self):
        if self.selling_price and self.expected_price:
            if float_compare(self.selling_price, self.expected_price * 0.9, precision_rounding=0.01) < 0:
                raise UserError('The selling price cannot be lower than 90% of the expected price.')
       