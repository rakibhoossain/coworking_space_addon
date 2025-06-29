# Coworking Space Module - Uninstall Fix Guide

## 🚨 Issue Description

**Error:** `KeyError: 'coworking.event.registration'` during module uninstallation

**Root Cause:** The database contains metadata references to removed custom models (`coworking.event` and `coworking.event.registration`) that no longer exist in the code. When Odoo tries to uninstall the module, it attempts to clean up data for these models but fails because the models are no longer defined.

## 🔧 Solution Options

### Option 1: SQL Script (Recommended - Fastest)

1. **Backup your database first!**
   ```bash
   pg_dump -U odoo -h localhost odoo_role > backup_before_cleanup.sql
   ```

2. **Connect to your PostgreSQL database:**
   ```bash
   psql -U odoo -h localhost -d odoo_role
   ```

3. **Run the cleanup SQL script:**
   ```sql
   \i /path/to/coworking_space/cleanup_database.sql
   ```

4. **Verify cleanup completed successfully**

5. **Try uninstalling the module again from Odoo**

### Option 2: Python Cleanup Script

1. **Update database configuration in `cleanup_before_uninstall.py`:**
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'port': 5432,
       'database': 'your_database_name',  # Update this
       'user': 'your_db_user',            # Update this
       'password': 'your_db_password',    # Update this
   }
   ```

2. **Install required Python package:**
   ```bash
   pip install psycopg2-binary
   ```

3. **Run the cleanup script:**
   ```bash
   cd /path/to/coworking_space/
   python3 cleanup_before_uninstall.py
   ```

4. **Try uninstalling the module again from Odoo**

### Option 3: Manual Database Cleanup

If you prefer to run the SQL commands manually:

```sql
-- Connect to your database and run these commands:

BEGIN;

-- Clean up ir_model_data entries
DELETE FROM ir_model_data WHERE model = 'coworking.event';
DELETE FROM ir_model_data WHERE model = 'coworking.event.registration';
DELETE FROM ir_model_data WHERE name LIKE 'model_coworking_event%';

-- Clean up ir_model entries
DELETE FROM ir_model WHERE model = 'coworking.event';
DELETE FROM ir_model WHERE model = 'coworking.event.registration';

-- Clean up ir_model_fields entries
DELETE FROM ir_model_fields WHERE model = 'coworking.event';
DELETE FROM ir_model_fields WHERE model = 'coworking.event.registration';

-- Clean up orphaned records
DELETE FROM mail_message WHERE model IN ('coworking.event', 'coworking.event.registration');
DELETE FROM mail_followers WHERE res_model IN ('coworking.event', 'coworking.event.registration');
DELETE FROM ir_attachment WHERE res_model IN ('coworking.event', 'coworking.event.registration');

COMMIT;
```

## 🔍 Verification Steps

After running any of the cleanup options, verify the cleanup was successful:

1. **Check for remaining references:**
   ```sql
   SELECT COUNT(*) FROM ir_model_data WHERE model IN ('coworking.event', 'coworking.event.registration');
   SELECT COUNT(*) FROM ir_model WHERE model IN ('coworking.event', 'coworking.event.registration');
   SELECT COUNT(*) FROM ir_model_fields WHERE model IN ('coworking.event', 'coworking.event.registration');
   ```

2. **All counts should be 0**

3. **Try uninstalling the module from Odoo interface**

## 🚀 Post-Cleanup Steps

1. **Uninstall the module:**
   - Go to Apps in Odoo
   - Search for "Coworking Space Management"
   - Click "Uninstall"
   - The uninstall should now complete without errors

2. **Verify clean uninstall:**
   - Check that no coworking_space related data remains
   - Verify no broken references in the system

## 🛡️ Prevention for Future

To prevent this issue in future module updates:

1. **Always use migration scripts when removing models**
2. **Test uninstallation in development environment**
3. **Use uninstall hooks for complex cleanup**
4. **Document model changes in migration notes**

## 📋 What Each Cleanup Method Does

### Database Tables Cleaned:
- `ir_model_data` - Removes metadata references to deleted models
- `ir_model` - Removes model definitions
- `ir_model_fields` - Removes field definitions
- `mail_message` - Removes orphaned messages
- `mail_followers` - Removes orphaned followers
- `ir_attachment` - Removes orphaned attachments

### Why This Works:
- Removes all database references to the deleted models
- Prevents Odoo from trying to access non-existent models during uninstall
- Cleans up orphaned data that could cause other issues

## 🆘 Troubleshooting

### If cleanup script fails:
1. Check database connection settings
2. Ensure you have sufficient database privileges
3. Verify database name and credentials
4. Check PostgreSQL service is running

### If uninstall still fails after cleanup:
1. Check Odoo logs for specific error details
2. Look for other model references we might have missed
3. Try restarting Odoo service after cleanup
4. Consider manual removal of remaining module data

### If you need to restore:
1. Stop Odoo service
2. Restore from backup: `psql -U odoo -d odoo_role < backup_before_cleanup.sql`
3. Start Odoo service
4. Try alternative cleanup method

## 📞 Support

If you continue to experience issues:
1. Check the Odoo logs for detailed error messages
2. Verify all custom model references have been updated
3. Consider seeking help from Odoo community forums
4. Contact your system administrator for database access issues

---

**Remember:** Always backup your database before performing any cleanup operations!
