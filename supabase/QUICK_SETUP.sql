-- ========================================
-- QUICK SETUP SCRIPT FOR LOGIMAS WITH RBAC
-- Run this after all migrations are complete
-- ========================================

-- Step 1: Verify all tables exist
SELECT 'Checking tables...' as status;
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('roles', 'permissions', 'role_permissions', 'user_roles', 
                     'customers', 'orders', 'shipments', 'vehicles', 'warehouses')
ORDER BY table_name;

-- Step 2: Check role-permission mappings
SELECT 'Checking role-permission mappings...' as status;
SELECT 
    r.role_name,
    COUNT(DISTINCT p.permission_id) as permission_count,
    STRING_AGG(p.permission_name, ', ' ORDER BY p.permission_name) as permissions
FROM roles r
JOIN role_permissions rp ON r.role_id = rp.role_id
JOIN permissions p ON rp.permission_id = p.permission_id
GROUP BY r.role_name
ORDER BY r.role_name;

-- Expected:
-- admin: 5 permissions (access_chat, access_knowledge_base, full_admin_access, perform_analysis, view_tracking)
-- customer: 3 permissions (access_chat, place_order, view_tracking)
-- delivery_person: 3 permissions (access_chat, report_incident, view_tracking)

-- Step 3: Create test users (if not already created)
-- NOTE: Create these users in Supabase Dashboard first, then run the role assignments below

-- Step 4: Assign roles to test users
-- Run these AFTER creating users in Supabase Dashboard

-- Admin role assignment
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.role_id
FROM auth.users u, roles r
WHERE u.email = 'admin@logimas.com' 
  AND r.role_name = 'admin'
ON CONFLICT DO NOTHING;

-- Delivery Person role assignment
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.role_id
FROM auth.users u, roles r
WHERE u.email = 'delivery@logimas.com' 
  AND r.role_name = 'delivery_person'
ON CONFLICT DO NOTHING;

-- Customer role assignment
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.role_id
FROM auth.users u, roles r
WHERE u.email = 'customer@logimas.com' 
  AND r.role_name = 'customer'
ON CONFLICT DO NOTHING;

-- Step 5: Verify user role assignments
SELECT 'Checking user role assignments...' as status;
SELECT 
    u.email,
    r.role_name,
    ur.assigned_at
FROM auth.users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.role_id
WHERE u.email LIKE '%@logimas.com'
ORDER BY u.email;

-- Step 6: Test permission functions
SELECT 'Testing permission functions...' as status;

-- Test get_user_permissions
SELECT 
    u.email,
    (SELECT ARRAY_AGG(permission_name) FROM get_user_permissions(u.id)) as permissions
FROM auth.users u
WHERE u.email LIKE '%@logimas.com'
ORDER BY u.email;

-- Step 7: View role statistics
SELECT 'Role Statistics:' as status;
SELECT * FROM role_statistics;

-- Step 8: Check role change audit log
SELECT 'Recent role changes:' as status;
SELECT 
    u.email,
    r_old.role_name as old_role,
    r_new.role_name as new_role,
    rca.changed_at,
    rca.reason
FROM role_change_audit rca
JOIN auth.users u ON rca.user_id = u.id
LEFT JOIN roles r_old ON rca.old_role_id = r_old.role_id
LEFT JOIN roles r_new ON rca.new_role_id = r_new.role_id
ORDER BY rca.changed_at DESC
LIMIT 10;

-- ========================================
-- SETUP COMPLETE!
-- ========================================

SELECT '✓ Setup verification complete!' as status;
SELECT 'Next steps:' as info;
SELECT '1. Start backend server' as step;
SELECT '2. Test API endpoints' as step;
SELECT '3. Login to frontend with different roles' as step;
