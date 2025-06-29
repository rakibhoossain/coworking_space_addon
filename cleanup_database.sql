-- SQL script to clean up removed coworking event models before uninstalling
-- Run this script directly in your PostgreSQL database before uninstalling the module

-- Start transaction
BEGIN;

-- Clean up ir_model_data entries for removed models
DELETE FROM ir_model_data WHERE model = 'coworking.event';
DELETE FROM ir_model_data WHERE model = 'coworking.event.registration';

-- Clean up ir_model_data entries with model references in name
DELETE FROM ir_model_data WHERE name LIKE 'model_coworking_event%';
DELETE FROM ir_model_data WHERE name LIKE 'model_coworking_event_registration%';

-- Clean up ir_model entries
DELETE FROM ir_model WHERE model = 'coworking.event';
DELETE FROM ir_model WHERE model = 'coworking.event.registration';

-- Clean up ir_model_fields entries
DELETE FROM ir_model_fields WHERE model = 'coworking.event';
DELETE FROM ir_model_fields WHERE model = 'coworking.event.registration';

-- Clean up orphaned mail records
DELETE FROM mail_message WHERE model IN ('coworking.event', 'coworking.event.registration');
DELETE FROM mail_followers WHERE res_model IN ('coworking.event', 'coworking.event.registration');

-- Clean up orphaned attachments
DELETE FROM ir_attachment WHERE res_model IN ('coworking.event', 'coworking.event.registration');

-- Clean up any remaining references in ir_model_data
DELETE FROM ir_model_data WHERE module = 'coworking_space' AND model IN ('coworking.event', 'coworking.event.registration');

-- Show what was cleaned up
SELECT 'Cleanup completed. Check the following counts:' as message;

SELECT 
    'ir_model_data entries remaining for removed models' as check_type,
    COUNT(*) as count 
FROM ir_model_data 
WHERE model IN ('coworking.event', 'coworking.event.registration');

SELECT 
    'ir_model entries remaining for removed models' as check_type,
    COUNT(*) as count 
FROM ir_model 
WHERE model IN ('coworking.event', 'coworking.event.registration');

SELECT 
    'ir_model_fields entries remaining for removed models' as check_type,
    COUNT(*) as count 
FROM ir_model_fields 
WHERE model IN ('coworking.event', 'coworking.event.registration');

-- Commit the transaction
COMMIT;

-- Display completion message
SELECT 'Database cleanup completed successfully. You can now uninstall the coworking_space module.' as result;
