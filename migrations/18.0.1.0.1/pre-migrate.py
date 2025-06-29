# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Clean up removed model references before uninstall"""
    _logger.info("Starting migration to clean up removed coworking event models")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # List of removed models that need cleanup
    removed_models = [
        'coworking.event',
        'coworking.event.registration',
    ]
    
    # Clean up ir.model.data entries for removed models
    for model_name in removed_models:
        _logger.info(f"Cleaning up ir.model.data entries for model: {model_name}")
        
        # Find and delete ir.model.data entries
        data_entries = env['ir.model.data'].search([
            ('model', '=', model_name)
        ])
        
        if data_entries:
            _logger.info(f"Found {len(data_entries)} ir.model.data entries for {model_name}")
            # Delete the entries to prevent uninstall issues
            data_entries.unlink()
            _logger.info(f"Deleted ir.model.data entries for {model_name}")
        
        # Clean up ir.model entries
        model_entries = env['ir.model'].search([
            ('model', '=', model_name)
        ])
        
        if model_entries:
            _logger.info(f"Found {len(model_entries)} ir.model entries for {model_name}")
            # Delete the model entries
            model_entries.unlink()
            _logger.info(f"Deleted ir.model entries for {model_name}")
        
        # Clean up ir.model.fields entries
        field_entries = env['ir.model.fields'].search([
            ('model', '=', model_name)
        ])
        
        if field_entries:
            _logger.info(f"Found {len(field_entries)} ir.model.fields entries for {model_name}")
            # Delete the field entries
            field_entries.unlink()
            _logger.info(f"Deleted ir.model.fields entries for {model_name}")
    
    # Clean up any remaining references in ir.model.data that point to these models
    _logger.info("Cleaning up any remaining references to removed models")
    
    # Clean up model references in ir.model.data
    for model_name in removed_models:
        # Clean up any data that references these models
        cr.execute("""
            DELETE FROM ir_model_data 
            WHERE model = %s 
            OR name LIKE %s
        """, (model_name, f'model_{model_name.replace(".", "_")}%'))
        
        deleted_count = cr.rowcount
        if deleted_count > 0:
            _logger.info(f"Deleted {deleted_count} additional ir.model.data entries for {model_name}")
    
    # Clean up any orphaned records that might reference the removed models
    _logger.info("Cleaning up orphaned records")
    
    # Clean up any mail.message records that might reference removed models
    cr.execute("""
        DELETE FROM mail_message 
        WHERE model IN %s
    """, (tuple(removed_models),))
    
    deleted_count = cr.rowcount
    if deleted_count > 0:
        _logger.info(f"Deleted {deleted_count} orphaned mail.message records")
    
    # Clean up any mail.followers records
    cr.execute("""
        DELETE FROM mail_followers 
        WHERE res_model IN %s
    """, (tuple(removed_models),))
    
    deleted_count = cr.rowcount
    if deleted_count > 0:
        _logger.info(f"Deleted {deleted_count} orphaned mail.followers records")
    
    # Clean up any ir.attachment records
    cr.execute("""
        DELETE FROM ir_attachment 
        WHERE res_model IN %s
    """, (tuple(removed_models),))
    
    deleted_count = cr.rowcount
    if deleted_count > 0:
        _logger.info(f"Deleted {deleted_count} orphaned ir.attachment records")
    
    # Clean up any workflow instances (if any)
    cr.execute("""
        DELETE FROM wkf_instance 
        WHERE res_type IN %s
    """, (tuple(removed_models),))
    
    deleted_count = cr.rowcount
    if deleted_count > 0:
        _logger.info(f"Deleted {deleted_count} orphaned workflow instances")
    
    # Commit the changes
    cr.commit()
    
    _logger.info("Migration completed successfully - removed model references cleaned up")
