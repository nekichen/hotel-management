# hotel_amenity/models/product_extension.py

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    amenity_id = fields.Many2one('hotel.amenity', string="Hotel Amenity", readonly=True, ondelete='cascade')
