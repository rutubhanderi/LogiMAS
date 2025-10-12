-- Migration to update role permissions to new configuration
-- This script removes old permission mappings and adds the correct ones

-- Step 1: Clear all existing role-permission mappings
DELETE FROM role_permissions;

-- Step 2: Assign NEW permissions to roles

-- Admin: Can access analysis, knowledge base, tracking, chat
-- CANNOT place orders or report incidents
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'admin' 
  AND p.permission_name IN ('view_tracking', 'access_knowledge_base', 'perform_analysis', 'access_chat', 'full_admin_access');

-- Delivery Person: Can report incidents, view tracking, chat
-- CANNOT place orders or access analysis
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'delivery_person' 
  AND p.permission_name IN ('view_tracking', 'report_incident', 'access_chat');

-- Customer: Can place orders, view tracking, chat
-- CANNOT access analysis or report incidents
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'customer' 
  AND p.permission_name IN ('place_order', 'view_tracking', 'access_chat');

-- Verification query (run this to check)
-- SELECT r.role_name, p.permission_name
-- FROM roles r
-- JOIN role_permissions rp ON r.role_id = rp.role_id
-- JOIN permissions p ON rp.permission_id = p.permission_id
-- ORDER BY r.role_name, p.permission_name;
