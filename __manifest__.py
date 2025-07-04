# -*- coding: utf-8 -*-
{
    'name': 'Coworking Space Management',
    'version': '18.0.1.0.0',
    'category': 'Services',
    'summary': 'Complete coworking space management with memberships, room booking, and events',
    'description': """
Coworking Space Management System
=================================

This module provides a comprehensive solution for managing coworking spaces including:

* **Membership Management**: Handle different subscription plans (Unlimited, Partial, Pay-As-You-Go)
* **Meeting Room Booking**: Allow members and non-members to book meeting rooms
* **Event Registration**: Manage events with online registration and payment
* **Automated Billing**: Generate monthly invoices with variable billing based on usage
* **Website Integration**: Portal for members and public booking interface

Features:
---------
* Multiple subscription plans with different pricing
* Real-time room availability checking
* Automated CRM opportunity creation for non-members
* Event management with payment integration
* Monthly automated billing with usage tracking
* Member portal access
* Payment integration (Stripe)

Subscription Plans:
------------------
* **Unlimited Plan (€20/month)**: Free access to coworking space, meeting rooms, and events
* **Partial Plan (€5/month)**: Free coworking access, paid meeting rooms (€1/hour), free/discounted events
* **Pay-As-You-Go (€10 for 10 hours)**: Credit-based system for coworking usage, paid events and meeting rooms
* **Non-members**: Custom quotes for meeting rooms, advance payment for events
    """,
    'author': 'Luminous Labs BD',
    'website': 'https://luminouslabsbd.com',
    'license': 'LGPL-3',
    'depends': [
        # Core Odoo modules (always available)
        'base',
        'website',
        'sale',
        'account',
        'crm',
        'portal',
        'calendar',
        'product',
        'calendar',
        'resource',

        # Event management (core modules)
        'event',
        'website_event',

        # E-commerce (usually available)
        'website_sale',
        'payment',
    ],
    'data': [
        # Security - Load first
        'security/ir.model.access.csv',
        'security/coworking_security.xml',

        # Core Views (using basic Odoo modules only)
        'views/event_event_views.xml',  # Extends Odoo's built-in event.event
        'views/coworking_membership_views.xml',
        'views/coworking_room_views.xml',
        'views/coworking_booking_views.xml',
        # 'views/coworking_event_views.xml',  # REMOVED: Using Odoo's event.event instead
        'views/coworking_usage_views.xml',
        'views/coworking_menus.xml',

        # Extended Views (commented out - require optional modules)
        # 'views/sale_subscription_views.xml',  # Requires sale_subscription
        # 'views/sale_rental_views.xml',        # Requires sale_renting

        # Data - Load after views
        'data/coworking_data.xml',
        'data/subscription_plans.xml',
        'data/website_data.xml',
        'data/email_templates.xml',

        # Website Templates - Load last
        'views/website_templates.xml',
        'views/portal_templates.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'coworking_space/static/src/css/coworking_frontend.css',
            'coworking_space/static/src/js/coworking_booking.js',
        ],
        'web.assets_backend': [
            'coworking_space/static/src/css/coworking_backend.css',
            'coworking_space/static/src/js/coworking_dashboard.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'images': ['static/description/banner.png'],
    'uninstall_hook': 'uninstall_hook',
}
