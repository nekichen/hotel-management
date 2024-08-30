from odoo import models, fields, api
from datetime import date

class HotelRooms(models.Model):
    _name = "hotel.rooms"
    _description = "Hotel Rooms"

    name = fields.Char(string="Room Name")
    room_status = fields.Selection(
        string="Room Status", 
        selection=[('available', 'Available'), ('reserved', 'Reserved'), ('occupied', 'Occupied')], 
        default='available'
    )
    is_room_avail = fields.Boolean(string="Is Room Available", default=True)
    
    floor = fields.Many2one('hotel.floors', string="Floor", ondelete='cascade')
    user_id = fields.Many2one('res.users', string="Room Manager")
    room_type = fields.Selection(string="Room Type", selection=[('single', 'Single'), ('double', 'Double')])
    rent = fields.Float(string="Rent")
    room_capacity = fields.Integer(string="Number of Persons")
    image = fields.Binary(string="Image")  # Perbaikan dari 'Im age' menjadi 'Image'
    room_description = fields.Text(string="Room Description")
    
    amenity_ids = fields.One2many('hotel.room.amenity', 'room_id', string="Amenities")
    
    cost = fields.Float(string="Cost", compute='_compute_subtotal', store=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Room name must be unique!'),
    ]
    
    @api.depends('amenity_ids')
    def _compute_subtotal(self):
        for room in self:
            room.cost = sum(room.amenity_ids.mapped('subtotal'))

    @api.onchange('room_status')
    def _check_room_availability(self):
        for room in self:
            room.is_room_avail = room.room_status == 'available'
    
    def update_room_status(self):
        for room in self:
            reservations = self.env['hotel.reservation'].search([
                ('room_ids.room_id', '=', room.id),
                ('reservation_status', '!=', 'cancelled')
            ])
            if not reservations:
                if room.room_status != 'available':
                    room.room_status = 'available'
            else:
                room_status_updated = False
                for reservation in reservations:
                    if reservation.checkout_date and date.today() > fields.Date.from_string(reservation.checkout_date):
                        if room.room_status != 'available':
                            room.room_status = 'available'
                            room_status_updated = True
                    else:
                        if room.room_status != 'reserved':
                            room.room_status = 'reserved'
                            room_status_updated = True
                
                if not room_status_updated:
                    continue

class HotelRoomAmenity(models.Model):
    _name = "hotel.room.amenity"
    _description = "Hotel Room Amenity"

    room_id = fields.Many2one('hotel.rooms', string="Room", required=True, ondelete='cascade')
    amenity_id = fields.Many2one('hotel.amenity', string="Amenity")
    quantity = fields.Integer(string="Quantity")
    price = fields.Float(string="Price")
    subtotal = fields.Float(string="Subtotal", compute='_compute_subtotal', store=True)
    
    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.price
