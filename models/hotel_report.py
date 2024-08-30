from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelReport(models.TransientModel):
    _name = 'hotel.report'
    _description = 'Hotel Report'

    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    room = fields.Many2one('hotel.rooms', string="Room")

    def action_generate_report(self):
        domain = [
            ('reservation_date', '>=', self.start_date),
            ('reservation_date', '<=', self.end_date)
        ]

        # Filter by room if a room is selected
        if self.room:
            domain.append(('room_ids.room_id', '=', self.room.id))

        reservations = self.env['hotel.reservation'].search(domain)

        if not reservations:
            raise ValidationError("No reservations found for the selected criteria.")

        return self.env.ref('hotel_management.action_hotel_report_pdf').report_action(reservations)
