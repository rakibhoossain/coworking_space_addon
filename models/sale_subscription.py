# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SaleSubscriptionTemplate(models.Model):
    """Extend subscription templates for coworking membership plans"""
    _inherit = 'sale.subscription.template'

    # Coworking-specific fields
    is_coworking_plan = fields.Boolean(
        string='Is Coworking Plan',
        default=False,
        help='Check if this subscription template is for coworking memberships'
    )
    
    coworking_access = fields.Selection([
        ('unlimited', 'Unlimited Access'),
        ('partial', 'Partial Access'),
        ('credit', 'Credit-based Access'),
    ], string='Coworking Access Type', help='Type of access to coworking space')
    
    meeting_room_access = fields.Selection([
        ('free', 'Free Access'),
        ('paid', 'Paid Access'),
        ('unavailable', 'No Access'),
    ], string='Meeting Room Access')
    
    event_access = fields.Selection([
        ('free', 'Free Access'),
        ('discounted', 'Discounted Access'),
        ('paid', 'Paid Access'),
    ], string='Event Access')
    
    credit_amount = fields.Float(
        string='Credit Amount (Hours)',
        help='Number of hours included in credit-based plans'
    )
    
    meeting_room_rate = fields.Float(
        string='Meeting Room Rate (€/hour)',
        help='Hourly rate for meeting room access'
    )


class SaleSubscription(models.Model):
    """Extend subscriptions for coworking memberships"""
    _inherit = 'sale.subscription'

    # Coworking-specific fields
    is_coworking_membership = fields.Boolean(
        string='Is Coworking Membership',
        compute='_compute_is_coworking_membership',
        store=True
    )
    
    credit_balance = fields.Float(
        string='Credit Balance (Hours)',
        default=0.0,
        help='Remaining credit hours for Pay-As-You-Go plans'
    )
    
    total_bookings = fields.Integer(
        string='Total Bookings',
        compute='_compute_usage_stats'
    )
    
    total_hours_used = fields.Float(
        string='Total Hours Used',
        compute='_compute_usage_stats'
    )
    
    # Related fields from template
    coworking_access = fields.Selection(
        related='template_id.coworking_access',
        readonly=True
    )
    
    meeting_room_access = fields.Selection(
        related='template_id.meeting_room_access',
        readonly=True
    )
    
    event_access = fields.Selection(
        related='template_id.event_access',
        readonly=True
    )

    @api.depends('template_id.is_coworking_plan')
    def _compute_is_coworking_membership(self):
        for subscription in self:
            subscription.is_coworking_membership = subscription.template_id.is_coworking_plan

    def _compute_usage_stats(self):
        """Compute usage statistics from related bookings and events"""
        for subscription in self:
            # Get rental orders (meeting room bookings)
            rental_orders = self.env['sale.rental'].search([
                ('partner_id', '=', subscription.partner_id.id),
                ('state', 'in', ['sale', 'done'])
            ])
            
            # Get event registrations
            event_registrations = self.env['event.registration'].search([
                ('partner_id', '=', subscription.partner_id.id),
                ('state', '=', 'done')
            ])
            
            subscription.total_bookings = len(rental_orders)
            subscription.total_hours_used = sum(rental_orders.mapped('duration'))

    def consume_credit(self, hours):
        """Consume credit hours for Pay-As-You-Go plans"""
        self.ensure_one()
        if self.coworking_access == 'credit':
            if self.credit_balance >= hours:
                self.credit_balance -= hours
                return True
            else:
                raise ValidationError(_('Insufficient credit balance. Current balance: %s hours') % self.credit_balance)
        return False

    def add_credit(self, hours):
        """Add credit hours to the membership"""
        self.ensure_one()
        if self.coworking_access == 'credit':
            self.credit_balance += hours

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set initial credit for Pay-As-You-Go plans"""
        subscriptions = super().create(vals_list)
        for subscription in subscriptions:
            if subscription.template_id.coworking_access == 'credit' and subscription.template_id.credit_amount:
                subscription.credit_balance = subscription.template_id.credit_amount
        return subscriptions

    def action_view_bookings(self):
        """View related room bookings"""
        self.ensure_one()
        return {
            'name': _('Room Bookings'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.rental',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {'default_partner_id': self.partner_id.id},
        }

    def action_view_events(self):
        """View related event registrations"""
        self.ensure_one()
        return {
            'name': _('Event Registrations'),
            'type': 'ir.actions.act_window',
            'res_model': 'event.registration',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {'default_partner_id': self.partner_id.id},
        }

    def _cron_check_expired_memberships(self):
        """Cron job to check and update expired memberships"""
        expired_subscriptions = self.search([
            ('is_coworking_membership', '=', True),
            ('stage_id.category', '=', 'progress'),
            ('date', '<', fields.Date.today())
        ])
        
        for subscription in expired_subscriptions:
            # Move to closed stage
            closed_stage = self.env['sale.subscription.stage'].search([
                ('category', '=', 'closed')
            ], limit=1)
            if closed_stage:
                subscription.stage_id = closed_stage.id
                
        _logger.info(f'Processed {len(expired_subscriptions)} expired coworking memberships')


class SaleSubscriptionStage(models.Model):
    """Extend subscription stages for coworking-specific stages"""
    _inherit = 'sale.subscription.stage'

    is_coworking_stage = fields.Boolean(
        string='Is Coworking Stage',
        default=False,
        help='Check if this stage is specific to coworking memberships'
    )
