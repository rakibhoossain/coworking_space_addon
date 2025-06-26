# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    """Extend events for coworking events"""
    _inherit = 'event.event'

    # Coworking-specific fields
    is_coworking_event = fields.Boolean(
        string='Is Coworking Event',
        default=False,
        help='Check if this is a coworking space event'
    )
    
    member_price = fields.Float(
        string='Member Price',
        help='Price for coworking members'
    )
    
    non_member_price = fields.Float(
        string='Non-Member Price',
        help='Price for non-members'
    )
    
    member_access = fields.Selection([
        ('free', 'Free for Members'),
        ('discounted', 'Discounted for Members'),
        ('paid', 'Paid for Members'),
    ], string='Member Access', default='free')
    
    location = fields.Char(
        string='Event Location',
        help='Physical location where the event takes place'
    )
    
    organizer_id = fields.Many2one(
        'res.partner',
        string='Event Organizer',
        help='Person or organization organizing the event'
    )
    
    # Statistics
    member_registrations = fields.Integer(
        string='Member Registrations',
        compute='_compute_registration_stats'
    )
    
    non_member_registrations = fields.Integer(
        string='Non-Member Registrations',
        compute='_compute_registration_stats'
    )

    @api.depends('registration_ids.is_member_registration')
    def _compute_registration_stats(self):
        for event in self:
            registrations = event.registration_ids.filtered(lambda r: r.state != 'cancel')
            event.member_registrations = len(registrations.filtered('is_member_registration'))
            event.non_member_registrations = len(registrations.filtered(lambda r: not r.is_member_registration))

    def get_price_for_partner(self, partner_id):
        """Get event price for a specific partner"""
        self.ensure_one()
        if not self.is_coworking_event:
            return 0.0  # Non-coworking events default to free

        if partner_id:
            # Check if partner has active coworking membership
            membership = self.env['coworking.membership'].search([
                ('partner_id', '=', partner_id),
                ('state', '=', 'active')
            ], limit=1)

            if membership:
                # Check event access type for members
                if membership.plan_id.event_access == 'free' or self.member_access == 'free':
                    return 0.0
                elif membership.plan_id.event_access == 'discounted' or self.member_access == 'discounted':
                    return self.member_price
                else:
                    return self.member_price or 0.0

        # Non-member price
        return self.non_member_price or 0.0

    def action_view_registrations(self):
        """View event registrations"""
        self.ensure_one()
        return {
            'name': _('Event Registrations'),
            'type': 'ir.actions.act_window',
            'res_model': 'event.registration',
            'view_mode': 'list,form',
            'domain': [('event_id', '=', self.id)],
            'context': {'default_event_id': self.id},
        }


class EventRegistration(models.Model):
    """Extend event registrations for coworking members"""
    _inherit = 'event.registration'

    # Coworking-specific fields
    membership_id = fields.Many2one(
        'coworking.membership',
        string='Membership',
        help='Related coworking membership'
    )
    
    is_member_registration = fields.Boolean(
        string='Is Member Registration',
        compute='_compute_is_member_registration',
        store=True
    )
    
    calculated_price = fields.Float(
        string='Calculated Price',
        compute='_compute_calculated_price',
        store=True
    )
    
    is_free = fields.Boolean(
        string='Is Free',
        compute='_compute_is_free',
        store=True
    )

    @api.depends('partner_id', 'membership_id')
    def _compute_is_member_registration(self):
        for registration in self:
            if registration.partner_id:
                membership = registration.membership_id or self.env['coworking.membership'].search([
                    ('partner_id', '=', registration.partner_id.id),
                    ('state', '=', 'active')
                ], limit=1)
                registration.is_member_registration = bool(membership)
                if membership and not registration.membership_id:
                    registration.membership_id = membership.id
            else:
                registration.is_member_registration = False

    @api.depends('event_id', 'partner_id', 'membership_id')
    def _compute_calculated_price(self):
        for registration in self:
            if registration.event_id and registration.event_id.is_coworking_event:
                registration.calculated_price = registration.event_id.get_price_for_partner(
                    registration.partner_id.id if registration.partner_id else None
                )
            else:
                # For non-coworking events, use 0.0 as default (events don't have standard_price)
                registration.calculated_price = 0.0

    @api.depends('calculated_price')
    def _compute_is_free(self):
        for registration in self:
            registration.is_free = registration.calculated_price == 0.0

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle coworking-specific logic"""
        for vals in vals_list:
            # Auto-set membership if partner has active membership
            if vals.get('partner_id') and not vals.get('membership_id'):
                membership = self.env['coworking.membership'].search([
                    ('partner_id', '=', vals['partner_id']),
                    ('state', '=', 'active')
                ], limit=1)
                if membership:
                    vals['membership_id'] = membership.id
        
        return super().create(vals_list)

    def action_confirm(self):
        """Confirm the registration"""
        for registration in self:
            # Check if event has available seats
            if registration.event_id.seats_max > 0 and registration.event_id.seats_available <= 0:
                raise ValidationError(_('No seats available for this event'))
                
            # For paid registrations, ensure payment is processed
            if not registration.is_free and registration.state == 'draft':
                # This would integrate with payment processing
                pass
                
        return super().action_confirm()

    def action_cancel(self):
        """Cancel the registration"""
        for registration in self:
            # Handle refunds if applicable
            if registration.is_member_registration and registration.calculated_price > 0:
                # Could implement refund logic here
                pass
                
        return super().action_cancel()


class EventType(models.Model):
    """Extend event types for coworking event categories"""
    _inherit = 'event.type'

    is_coworking_type = fields.Boolean(
        string='Is Coworking Type',
        default=False,
        help='Check if this event type is for coworking events'
    )
    
    default_member_access = fields.Selection([
        ('free', 'Free for Members'),
        ('discounted', 'Discounted for Members'),
        ('paid', 'Paid for Members'),
    ], string='Default Member Access', default='free')
    
    default_member_price = fields.Float(
        string='Default Member Price',
        help='Default price for coworking members'
    )
    
    default_non_member_price = fields.Float(
        string='Default Non-Member Price',
        help='Default price for non-members'
    )
