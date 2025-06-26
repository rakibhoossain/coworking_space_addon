# -*- coding: utf-8 -*-

# Core models that work with basic Odoo installation
from . import event_event
from . import res_partner
from . import sale_order

# Custom models (fallback approach for basic functionality)
from . import coworking_membership
from . import coworking_room
from . import coworking_booking
# from . import coworking_event  # REMOVED: Using Odoo's built-in event.event instead
from . import coworking_usage
from . import coworking_invoice

# Extended models (commented out - require optional modules)
# These will be loaded only if the required modules are installed
# from . import sale_subscription  # Requires sale_subscription module
# from . import sale_rental        # Requires sale_renting module - CAUSES ERRORS
