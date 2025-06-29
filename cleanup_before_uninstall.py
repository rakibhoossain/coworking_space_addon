#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual cleanup script to run before uninstalling coworking_space module.

This script cleans up database references to removed models that cause
KeyError during module uninstallation.

Usage:
1. Run this script before uninstalling the module
2. Then proceed with normal module uninstallation

Run with:
python3 cleanup_before_uninstall.py
"""

import psycopg2
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)

# Database configuration - UPDATE THESE VALUES
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'odoo_role',  # Change to your database name
    'user': 'odoo',           # Change to your database user
    'password': 'odoo',       # Change to your database password
}

def cleanup_removed_models():
    """Clean up database references to removed coworking event models"""
    
    # List of removed models that need cleanup
    removed_models = [
        'coworking.event',
        'coworking.event.registration',
    ]
    
    try:
        # Connect to database
        _logger.info("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        _logger.info("Starting cleanup of removed model references")
        
        # Clean up ir.model.data entries
        for model_name in removed_models:
            _logger.info(f"Cleaning up ir_model_data entries for model: {model_name}")
            
            # Delete ir.model.data entries
            cursor.execute("""
                DELETE FROM ir_model_data 
                WHERE model = %s
            """, (model_name,))
            
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                _logger.info(f"Deleted {deleted_count} ir_model_data entries for {model_name}")
            
            # Delete entries with model references in name
            cursor.execute("""
                DELETE FROM ir_model_data 
                WHERE name LIKE %s
            """, (f'model_{model_name.replace(".", "_")}%',))
            
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                _logger.info(f"Deleted {deleted_count} additional ir_model_data entries for {model_name}")
        
        # Clean up ir.model entries
        for model_name in removed_models:
            _logger.info(f"Cleaning up ir_model entries for model: {model_name}")
            
            cursor.execute("""
                DELETE FROM ir_model 
                WHERE model = %s
            """, (model_name,))
            
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                _logger.info(f"Deleted {deleted_count} ir_model entries for {model_name}")
        
        # Clean up ir.model.fields entries
        for model_name in removed_models:
            _logger.info(f"Cleaning up ir_model_fields entries for model: {model_name}")
            
            cursor.execute("""
                DELETE FROM ir_model_fields 
                WHERE model = %s
            """, (model_name,))
            
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                _logger.info(f"Deleted {deleted_count} ir_model_fields entries for {model_name}")
        
        # Clean up orphaned records
        _logger.info("Cleaning up orphaned records")
        
        # Clean up mail.message records
        cursor.execute("""
            DELETE FROM mail_message 
            WHERE model IN %s
        """, (tuple(removed_models),))
        
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            _logger.info(f"Deleted {deleted_count} orphaned mail_message records")
        
        # Clean up mail.followers records
        cursor.execute("""
            DELETE FROM mail_followers 
            WHERE res_model IN %s
        """, (tuple(removed_models),))
        
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            _logger.info(f"Deleted {deleted_count} orphaned mail_followers records")
        
        # Clean up ir.attachment records
        cursor.execute("""
            DELETE FROM ir_attachment 
            WHERE res_model IN %s
        """, (tuple(removed_models),))
        
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            _logger.info(f"Deleted {deleted_count} orphaned ir_attachment records")
        
        # Clean up any remaining references in other tables
        _logger.info("Cleaning up any remaining references")
        
        # Check for any remaining references
        for model_name in removed_models:
            cursor.execute("""
                SELECT table_name, column_name 
                FROM information_schema.columns 
                WHERE column_default LIKE %s
                OR column_name LIKE %s
            """, (f'%{model_name}%', f'%{model_name.replace(".", "_")}%'))
            
            remaining_refs = cursor.fetchall()
            if remaining_refs:
                _logger.warning(f"Found remaining references to {model_name}: {remaining_refs}")
        
        # Commit all changes
        conn.commit()
        _logger.info("All cleanup operations completed successfully")
        
        # Close connection
        cursor.close()
        conn.close()
        
        _logger.info("Database cleanup completed. You can now safely uninstall the coworking_space module.")
        
    except psycopg2.Error as e:
        _logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        _logger.error(f"Unexpected error: {e}")
        return False
    
    return True

def main():
    """Main function"""
    _logger.info("Coworking Space Module - Database Cleanup Script")
    _logger.info("=" * 50)
    
    # Confirm before proceeding
    print("\nThis script will clean up database references to removed coworking event models.")
    print("Make sure to backup your database before proceeding!")
    print(f"Database: {DB_CONFIG['database']} on {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    
    confirm = input("\nDo you want to proceed? (yes/no): ").lower().strip()
    if confirm not in ['yes', 'y']:
        print("Operation cancelled.")
        return
    
    # Run cleanup
    success = cleanup_removed_models()
    
    if success:
        print("\n✅ Cleanup completed successfully!")
        print("You can now safely uninstall the coworking_space module from Odoo.")
    else:
        print("\n❌ Cleanup failed. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
