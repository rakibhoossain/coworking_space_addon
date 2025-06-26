# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """Extend products for meeting rooms"""
    _inherit = 'product.product'

    # Meeting room specific fields
    is_meeting_room = fields.Boolean(
        string='Is Meeting Room',
        default=False,
        help='Check if this product represents a meeting room'
    )
    
    room_capacity = fields.Integer(
        string='Room Capacity',
        help='Maximum number of people the room can accommodate'
    )
    
    room_equipment = fields.Text(
        string='Equipment & Amenities',
        help='List of equipment and amenities available in the room'
    )
    
    room_location = fields.Char(
        string='Room Location',
        help='Physical location of the room'
    )
    
    available_days = fields.Selection([
        ('all', 'All Days'),
        ('weekdays', 'Weekdays Only'),
        ('weekends', 'Weekends Only'),
        ('custom', 'Custom Schedule'),
    ], string='Available Days', default='all')
    
    available_from = fields.Float(
        string='Available From (Hour)',
        default=8.0,
        help='Start time for room availability (24-hour format)'
    )
    
    available_to = fields.Float(
        string='Available To (Hour)',
        default=20.0,
        help='End time for room availability (24-hour format)'
    )
    
    member_rate = fields.Float(
        string='Member Rate (€/hour)',
        help='Hourly rate for members'
    )
    
    non_member_rate = fields.Float(
        string='Non-Member Rate (€/hour)',
        help='Hourly rate for non-members'
    )

    @api.constrains('room_capacity')
    def _check_room_capacity(self):
        for room in self:
            if room.is_meeting_room and room.room_capacity <= 0:
                raise ValidationError(_('Room capacity must be greater than 0'))

    def get_hourly_rate(self, partner_id=None):
        """Get hourly rate based on partner membership status"""
        self.ensure_one()
        if not self.is_meeting_room:
            return 0.0
            
        if partner_id:
            # Check if partner has active coworking membership
            membership = self.env['sale.subscription'].search([
                ('partner_id', '=', partner_id),
                ('is_coworking_membership', '=', True),
                ('stage_id.category', '=', 'progress')
            ], limit=1)
            
            if membership:
                # Check meeting room access type
                if membership.meeting_room_access == 'free':
                    return 0.0
                elif membership.meeting_room_access == 'paid':
                    return self.member_rate or membership.template_id.meeting_room_rate or 1.0
                    
        # Non-member or no membership
        return self.non_member_rate or self.list_price

    def is_available(self, start_datetime, end_datetime):
        """Check if room is available for the given time period"""
        self.ensure_one()
        if not self.is_meeting_room:
            return False
            
        # Check existing rentals
        existing_rentals = self.env['sale.rental'].search([
            ('product_id', '=', self.id),
            ('state', 'in', ['sale', 'done']),
            '|',
            '&', ('pickup_date', '<=', start_datetime), ('return_date', '>', start_datetime),
            '&', ('pickup_date', '<', end_datetime), ('return_date', '>=', end_datetime),
        ])
        
        return len(existing_rentals) == 0


class SaleRental(models.Model):
    """Extend rental orders for meeting room bookings"""
    _inherit = 'sale.rental'

    # Coworking-specific fields
    is_coworking_booking = fields.Boolean(
        string='Is Coworking Booking',
        compute='_compute_is_coworking_booking',
        store=True
    )
    
    membership_id = fields.Many2one(
        'sale.subscription',
        string='Membership',
        help='Related coworking membership'
    )
    
    booking_type = fields.Selection([
        ('member', 'Member Booking'),
        ('non_member', 'Non-Member Booking'),
    ], string='Booking Type', compute='_compute_booking_type', store=True)
    
    crm_lead_id = fields.Many2one(
        'crm.lead',
        string='CRM Opportunity',
        help='Related CRM opportunity for non-member bookings'
    )
    
    duration_hours = fields.Float(
        string='Duration (Hours)',
        compute='_compute_duration_hours',
        store=True
    )

    @api.depends('product_id.is_meeting_room')
    def _compute_is_coworking_booking(self):
        for rental in self:
            rental.is_coworking_booking = rental.product_id.is_meeting_room

    @api.depends('partner_id')
    def _compute_booking_type(self):
        for rental in self:
            if rental.partner_id:
                membership = self.env['sale.subscription'].search([
                    ('partner_id', '=', rental.partner_id.id),
                    ('is_coworking_membership', '=', True),
                    ('stage_id.category', '=', 'progress')
                ], limit=1)
                rental.booking_type = 'member' if membership else 'non_member'
                rental.membership_id = membership.id if membership else False
            else:
                rental.booking_type = 'non_member'

    @api.depends('pickup_date', 'return_date')
    def _compute_duration_hours(self):
        for rental in self:
            if rental.pickup_date and rental.return_date:
                duration = rental.return_date - rental.pickup_date
                rental.duration_hours = duration.total_seconds() / 3600
            else:
                rental.duration_hours = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle coworking-specific logic"""
        rentals = super().create(vals_list)
        
        for rental in rentals:
            if rental.is_coworking_booking:
                # Auto-set membership if partner has active membership
                if rental.partner_id and not rental.membership_id:
                    membership = self.env['sale.subscription'].search([
                        ('partner_id', '=', rental.partner_id.id),
                        ('is_coworking_membership', '=', True),
                        ('stage_id.category', '=', 'progress')
                    ], limit=1)
                    if membership:
                        rental.membership_id = membership.id
                
                # Create CRM opportunity for non-member bookings
                if rental.booking_type == 'non_member' and not rental.crm_lead_id:
                    lead_vals = {
                        'name': f'Meeting Room Booking (Non-Member) - {rental.product_id.name}',
                        'partner_id': rental.partner_id.id,
                        'email_from': rental.partner_id.email,
                        'phone': rental.partner_id.phone,
                        'description': f'Non-member booking for {rental.product_id.name} from {rental.pickup_date} to {rental.return_date}',
                        'stage_id': self.env['crm.stage'].search([('is_won', '=', False)], limit=1).id,
                        'team_id': self.env['crm.team'].search([], limit=1).id,
                        'user_id': self.env.user.id,
                    }
                    lead = self.env['crm.lead'].create(lead_vals)
                    rental.crm_lead_id = lead.id
                    
        return rentals

    def action_confirm(self):
        """Confirm the booking"""
        for rental in self:
            if rental.is_coworking_booking:
                # Check room availability
                if not rental.product_id.is_available(rental.pickup_date, rental.return_date):
                    raise ValidationError(_('Room is not available for the selected time period'))
                
                # For member bookings with credit-based plans, consume credits
                if rental.membership_id and rental.membership_id.coworking_access == 'credit':
                    if rental.membership_id.meeting_room_access == 'paid':
                        try:
                            rental.membership_id.consume_credit(rental.duration_hours)
                        except ValidationError:
                            raise UserError(_('Insufficient credit balance for this booking'))
                            
        return super().action_confirm()

    def action_view_crm_lead(self):
        """View related CRM opportunity"""
        self.ensure_one()
        if self.crm_lead_id:
            return {
                'name': _('CRM Opportunity'),
                'type': 'ir.actions.act_window',
                'res_model': 'crm.lead',
                'res_id': self.crm_lead_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def _cron_auto_complete_bookings(self):
        """Cron job to auto-complete past bookings"""
        past_bookings = self.search([
            ('is_coworking_booking', '=', True),
            ('state', '=', 'sale'),
            ('return_date', '<', datetime.now())
        ])
        
        for booking in past_bookings:
            booking.action_return()
            
        _logger.info(f'Auto-completed {len(past_bookings)} past bookings')
