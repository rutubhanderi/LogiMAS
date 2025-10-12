-- ========================================
-- COMPLETE DATABASE SETUP WITH RBAC INTEGRATION
-- This script ensures all tables work together properly
-- ========================================

-- Step 1: Ensure customers table references auth.users properly
-- Add user_id column to customers table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'customers' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE customers ADD COLUMN user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE;
        CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);
    END IF;
END $$;

-- Step 2: Ensure orders table has proper status tracking
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'orders' AND column_name = 'created_by'
    ) THEN
        ALTER TABLE orders ADD COLUMN created_by uuid REFERENCES auth.users(id);
        CREATE INDEX IF NOT EXISTS idx_orders_created_by ON orders(created_by);
    END IF;
END $$;

-- Step 3: Add incident reporter tracking to documents table
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'documents' AND column_name = 'reported_by'
    ) THEN
        ALTER TABLE documents ADD COLUMN reported_by uuid REFERENCES auth.users(id);
        CREATE INDEX IF NOT EXISTS idx_documents_reported_by ON documents(reported_by);
    END IF;
END $$;

-- Step 4: Add user tracking to agent_audit_logs
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'agent_audit_logs' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE agent_audit_logs ADD COLUMN user_id uuid REFERENCES auth.users(id);
        CREATE INDEX IF NOT EXISTS idx_agent_audit_logs_user_id ON agent_audit_logs(user_id);
    END IF;
END $$;

-- Step 5: Create a view for user permissions (for easy querying)
CREATE OR REPLACE VIEW user_permissions_view AS
SELECT 
    u.id as user_id,
    u.email,
    r.role_name,
    p.permission_name
FROM auth.users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.role_id
JOIN role_permissions rp ON r.role_id = rp.role_id
JOIN permissions p ON rp.permission_id = p.permission_id;

-- Step 6: Create a function to check if a user can perform an action
CREATE OR REPLACE FUNCTION can_user_perform_action(
    user_uuid uuid,
    action_name text
)
RETURNS boolean AS $$
BEGIN
    -- Check if user has the required permission
    RETURN EXISTS (
        SELECT 1
        FROM user_roles ur
        JOIN role_permissions rp ON ur.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.permission_id
        WHERE ur.user_id = user_uuid 
        AND p.permission_name = action_name
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 7: Create audit log for role changes
CREATE TABLE IF NOT EXISTS role_change_audit (
    audit_id bigserial PRIMARY KEY,
    user_id uuid REFERENCES auth.users(id),
    old_role_id uuid REFERENCES roles(role_id),
    new_role_id uuid REFERENCES roles(role_id),
    changed_by uuid REFERENCES auth.users(id),
    changed_at timestamptz DEFAULT now(),
    reason text
);

CREATE INDEX IF NOT EXISTS idx_role_change_audit_user ON role_change_audit(user_id);
CREATE INDEX IF NOT EXISTS idx_role_change_audit_changed_at ON role_change_audit(changed_at DESC);

-- Step 8: Create trigger to log role changes
CREATE OR REPLACE FUNCTION log_role_change()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO role_change_audit (user_id, new_role_id, changed_by, reason)
        VALUES (NEW.user_id, NEW.role_id, NEW.user_id, 'Role assigned');
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO role_change_audit (user_id, old_role_id, new_role_id, changed_by, reason)
        VALUES (NEW.user_id, OLD.role_id, NEW.role_id, NEW.user_id, 'Role updated');
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO role_change_audit (user_id, old_role_id, changed_by, reason)
        VALUES (OLD.user_id, OLD.role_id, OLD.user_id, 'Role removed');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_log_role_change ON user_roles;
CREATE TRIGGER trigger_log_role_change
    AFTER INSERT OR UPDATE OR DELETE ON user_roles
    FOR EACH ROW
    EXECUTE FUNCTION log_role_change();

-- Step 9: Create helper function to get user's full profile with role
CREATE OR REPLACE FUNCTION get_user_profile(user_uuid uuid)
RETURNS TABLE (
    user_id uuid,
    email text,
    role_name text,
    permissions text[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.email::text,
        r.role_name,
        ARRAY_AGG(DISTINCT p.permission_name) as permissions
    FROM auth.users u
    LEFT JOIN user_roles ur ON u.id = ur.user_id
    LEFT JOIN roles r ON ur.role_id = r.role_id
    LEFT JOIN role_permissions rp ON r.role_id = rp.role_id
    LEFT JOIN permissions p ON rp.permission_id = p.permission_id
    WHERE u.id = user_uuid
    GROUP BY u.id, u.email, r.role_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 10: Create function to assign default customer role to new users
CREATE OR REPLACE FUNCTION assign_default_role()
RETURNS TRIGGER AS $$
BEGIN
    -- Automatically assign 'customer' role to new users
    INSERT INTO user_roles (user_id, role_id)
    SELECT NEW.id, role_id
    FROM roles
    WHERE role_name = 'customer'
    ON CONFLICT DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS trigger_assign_default_role ON auth.users;
CREATE TRIGGER trigger_assign_default_role
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION assign_default_role();

-- Step 11: Create materialized view for role statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS role_statistics AS
SELECT 
    r.role_name,
    r.description,
    COUNT(DISTINCT ur.user_id) as user_count,
    COUNT(DISTINCT rp.permission_id) as permission_count,
    ARRAY_AGG(DISTINCT p.permission_name ORDER BY p.permission_name) as permissions
FROM roles r
LEFT JOIN user_roles ur ON r.role_id = ur.role_id
LEFT JOIN role_permissions rp ON r.role_id = rp.role_id
LEFT JOIN permissions p ON rp.permission_id = p.permission_id
GROUP BY r.role_id, r.role_name, r.description;

CREATE UNIQUE INDEX IF NOT EXISTS idx_role_statistics_role_name ON role_statistics(role_name);

-- Function to refresh role statistics
CREATE OR REPLACE FUNCTION refresh_role_statistics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY role_statistics;
END;
$$ LANGUAGE plpgsql;

-- Step 12: Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_agent_audit_logs_timestamp ON agent_audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_documents_source_type ON documents(source_type);
CREATE INDEX IF NOT EXISTS idx_documents_ts ON documents(ts DESC);

-- Step 13: Grant necessary permissions (if using RLS in future)
-- These are commented out since RLS is not enabled
-- GRANT SELECT ON roles TO authenticated;
-- GRANT SELECT ON permissions TO authenticated;
-- GRANT SELECT ON role_permissions TO authenticated;
-- GRANT SELECT ON user_roles TO authenticated;

-- ========================================
-- VERIFICATION QUERIES
-- ========================================

-- Uncomment to run verification after migration

-- Check all tables exist
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- ORDER BY table_name;

-- Check role distribution
-- SELECT * FROM role_statistics;

-- Check a specific user's profile
-- SELECT * FROM get_user_profile('YOUR_USER_ID_HERE');

-- Check user permissions view
-- SELECT * FROM user_permissions_view LIMIT 10;

-- ========================================
-- MIGRATION COMPLETE
-- ========================================
