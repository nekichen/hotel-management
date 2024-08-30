from odoo import api, fields, models

class HotelReservation(models.Model):
    _name = "hotel.reservation"
    _description = "Hotel Reservation"

    reservation_code = fields.Char(string="Reservation Code", required=True, copy=False, readonly=True, index=True, default="New")
    reservation_date = fields.Date(string="Reservation Date", default=lambda self: fields.Date.context_today(self))
    customer = fields.Many2one('res.partner', string="Customer")
    reservation_status = fields.Selection(
        string="Status",
        selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ('checkin', 'Checked in'), ('checkout', 'Checked out'), ('cancelled', 'Cancelled')],
        default='draft'
    )
    
    room_ids = fields.One2many('hotel.book.room', 'reservation_id', ondelete='cascade')
    checkin_date = fields.Datetime(string="Checkin Date")
    checkout_date = fields.Datetime(string="Checkout Date")
    total_days = fields.Integer(string="Total Days", compute='_compute_total_days', store=True)
    subtotal = fields.Float(string="Subtotal", compute='_compute_subtotal', store=True)
    note = fields.Text(string="Note")

    _sql_constraints = [
        ('reservation_code_uniq', 'unique(reservation_code)', 'Reservation code must be unique!'),
    ]

    def action_confirm(self):
        for reservation in self:
            if reservation.reservation_status == 'draft':
                reservation.reservation_status = 'confirmed'
                reservation.reservation_code = self._generate_reservation_code()
                
                # Update room status to 'reserved'
                for room in reservation.room_ids:
                    if room.room_id:
                        room.room_id.room_status = 'reserved'
                        
    def action_checkin(self):
        for reservation in self:
            if reservation.reservation_status == 'confirmed':
                reservation.reservation_status = 'checkin'
                
                for room in reservation.room_ids:
                    if room.room_id:
                        room.room_id.room_status = 'occupied'

    def action_checkout(self):
        for reservation in self:
            if reservation.reservation_status == 'checkin':
                reservation.reservation_status = 'checkout'
                
                for room in reservation.room_ids:
                    if room.room_id:
                        room.room_id.room_status = 'available'

    def action_cancel(self):
        for reservation in self:
            if reservation.reservation_status in ['draft', 'confirmed']:
                reservation.reservation_status = 'cancelled'
                
                # Update room status to 'available'
                for room in reservation.room_ids:
                    if room.room_id:
                        room.room_id.room_status = 'available'

    def _generate_reservation_code(self):
        last_reservation = self.search([('reservation_code', '!=', 'New')], order='id desc', limit=1)
        if last_reservation:
            last_code = last_reservation.reservation_code
            last_number = int(last_code.split('/')[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        new_code = 'BOOKING/{:06d}'.format(new_number)
        return new_code

    @api.depends('checkin_date', 'checkout_date')
    def _compute_total_days(self):
        for reservation in self:
            if reservation.checkin_date and reservation.checkout_date:
                checkin_date = fields.Date.from_string(reservation.checkin_date)
                checkout_date = fields.Date.from_string(reservation.checkout_date)
                reservation.total_days = (checkout_date - checkin_date).days
            else:
                reservation.total_days = 0

    @api.depends('room_ids', 'total_days')
    def _compute_subtotal(self):
        for reservation in self:
            if reservation.reservation_status == 'cancelled':
                reservation.subtotal = 0
            elif reservation.total_days == 0:
                reservation.subtotal = sum(room.rent for room in reservation.room_ids if room.rent)
            else:
                reservation.subtotal = sum(room.rent * reservation.total_days for room in reservation.room_ids if room.rent)
    
    def unlink(self):
        for reservation in self:
            # Update room status when reservations are deleted
            for room in reservation.room_ids:
                if room.room_id:
                    room.room_id.update_room_status()
        return super(HotelReservation, self).unlink()

class HotelBookRoom(models.Model):
    _name = "hotel.book.room"
    _description = "Hotel Book Room"

    reservation_id = fields.Many2one('hotel.reservation', string="Reservation", ondelete='cascade')
    room_id = fields.Many2one('hotel.rooms', string="Room", ondelete='cascade')
    rent = fields.Float(related='room_id.rent', string="Rent", readonly=True)
