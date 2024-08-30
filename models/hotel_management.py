from odoo import api, fields, models

class HotelFloors(models.Model):
    _name = "hotel.floors"
    _description = "Hotel Floors"

    name = fields.Char(string="Floor Name")
    manager = fields.Many2one('res.partner', string="Manager")
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Floor name must be unique!'),
    ]

class HotelAmenity(models.Model):
    _name = "hotel.amenity"
    _description = "Hotel Amenity"

    name = fields.Char(string="Amenity Name", required=True)
    image = fields.Binary(string="Image")
    product_id = fields.Many2one('product.template', string="Linked Product", readonly=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Amenity name must be unique!'),
    ]

    @api.model
    def create(self, vals):
        # Create the hotel amenity
        amenity = super(HotelAmenity, self).create(vals)

        # Create a corresponding product in the inventory
        product_vals = {
            'name': amenity.name,
            'type': 'product',  # Assuming amenities are tangible products
            'image_1920': amenity.image,  # Use Odoo's field for product images
            'amenity_id': amenity.id,  # Link back to the amenity
        }
        product = self.env['product.template'].create(product_vals)

        # Link the created product to the amenity
        amenity.product_id = product.id

        return amenity
    
class HotelServices(models.Model):
    _name = "hotel.services"
    _description = "Hotel Services"

    name = fields.Char(string="Service Name")
    price = fields.Float(string="Price")
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Service name must be unique!'),
    ]
