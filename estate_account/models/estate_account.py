from odoo import models, fields, api
from odoo.exceptions import UserError

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    def action_sold(self):
        res = super(EstateProperty, self).action_sold()
        for property in self:
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice', # Customer Invoice
                'partner_id': property.buyer_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [
                    (0, 0, {
                        'name': 'Selling Price (6%)',
                        'quantity': 1,
                        'price_unit': property.selling_price * 0.06,
                    }),
                    (0, 0, {
                        'name': 'Administrative Fees',
                        'quantity': 1,
                        'price_unit': 100.00,
                    }),
                ],
            })
            property.invoice_id = invoice.id
        return res