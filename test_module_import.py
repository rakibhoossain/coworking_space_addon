#!/usr/bin/env python3
"""
Test script to check if the coworking_space module can be imported correctly
"""

import sys
import os

# Add the odoo path to sys.path
odoo_path = '/Users/rakib/Projects/luminouslabsbd/odoo-18.0.latest'
sys.path.insert(0, odoo_path)

try:
    # Try to import the module components
    print("Testing module imports...")
    
    # Test model imports
    print("1. Testing model imports...")
    from odoo.addons.coworking_space.models import coworking_membership
    print("   ✓ coworking_membership imported")
    
    from odoo.addons.coworking_space.models import coworking_room
    print("   ✓ coworking_room imported")
    
    from odoo.addons.coworking_space.models import coworking_booking
    print("   ✓ coworking_booking imported")
    
    from odoo.addons.coworking_space.models import coworking_event
    print("   ✓ coworking_event imported")
    
    from odoo.addons.coworking_space.models import coworking_usage
    print("   ✓ coworking_usage imported")
    
    from odoo.addons.coworking_space.models import coworking_invoice
    print("   ✓ coworking_invoice imported")
    
    # Test controller imports
    print("2. Testing controller imports...")
    from odoo.addons.coworking_space.controllers import booking
    print("   ✓ booking controller imported")
    
    from odoo.addons.coworking_space.controllers import portal
    print("   ✓ portal controller imported")
    
    from odoo.addons.coworking_space.controllers import main
    print("   ✓ main controller imported")
    
    # Test wizard imports
    print("3. Testing wizard imports...")
    from odoo.addons.coworking_space.wizard import generate_monthly_invoices
    print("   ✓ generate_monthly_invoices wizard imported")
    
    print("\n🎉 All imports successful! Module structure is correct.")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
