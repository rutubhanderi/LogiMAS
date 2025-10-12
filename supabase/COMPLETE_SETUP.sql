-- ========================================
-- COMPLETE LOGIMAS DATABASE SETUP
-- Run this entire script in Supabase SQL Editor
-- ========================================

-- ========================================
-- PART 1: INITIAL SCHEMA
-- ========================================

-- Enable the pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the customers table
CREATE TABLE IF NOT EXISTS customers (
  customer_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  name text,
  phone text,
  address jsonb,
  loyalty_tier text,
  created_at timestamptz DEFAULT now()
);

-- Create the orders table
CREATE TABLE IF NOT EXISTS orders (
  order_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid REFERENCES customers(customer_id),
  order_date timestamptz,
  order_total numeric,
  items jsonb,
  destination jsonb,
  status text,
  estimated_delivery_date timestamptz,
  actual_delivery_date timestamptz
);

-- Create the warehouses table
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    lat double precision,
    lon double precision,
    region text
);

-- Create the vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_type text,
    capacity_kg numeric,
    capacity_volume_cm3 numeric,
    fuel_type text,
    status text
);

-- Create the shipments table
CREATE TABLE IF NOT EXISTS shipments (
  shipment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid REFERENCES orders(order_id),
  origin_warehouse_id uuid REFERENCES warehouses(warehouse_id),
  vehicle_id uuid REFERENCES vehicles(vehicle_id),
  shipped_at timestamptz,
  expected_arrival timestamptz,
  current_eta timestamptz,
  status text,
  distance_km numeric
);

-- Create the vehicle_telemetry table (time-series data)
CREATE TABLE IF NOT EXISTS vehicle_telemetry (
    id bigserial PRIMARY KEY,
    vehicle_id uuid REFERENCES vehicles(vehicle_id),
    ts timestamptz NOT NULL,
    lat double precision,
    lon double precision,
    speed_kmph numeric,
    fuel_pct numeric,
    cargo_temp numeric
);

-- Create agent_audit_logs table
CREATE TABLE IF NOT EXISTS agent_audit_logs (
    log_id bigserial PRIMARY KEY,
    agent_name text NOT NULL,
    decision_json jsonb,
    confidence numeric,
    timestamp timestamptz DEFAULT now(),
    input_context jsonb
);

-- Create the documents table for RAG with a vector column
CREATE TABLE IF NOT EXISTS documents (
    doc_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type text,
    source_id text,
    region_id text,
    ts timestamptz,
    chunk_index integer,
    text_snippet text,
    embedding_model text,
    embedding vector(768)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_ts ON vehicle_telemetry(vehicle_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_shipments_status_eta ON shipments(status, current_eta);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING hnsw (embedding vector_l2_ops);

-- ========================================
-- PART 2: RBAC SCHEMA
-- ========================================

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
  role_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  role_name text UNIQUE NOT NULL,
  description text,
  created_at timestamptz DEFAULT now()
);

-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
  permission_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  permission_name text UNIQUE NOT NULL,
  description text,
  created_at timestamptz DEFAULT now()
);

-- Create role_permissions junction table
CREATE TABLE IF NOT EXISTS role_permissions (
  role_id uuid REFERENCES roles(role_id) ON DELETE CASCADE,
  permission_id uuid REFERENCES permissions(permission_id) ON DELETE CASCADE,
  PRIMARY KEY (role_id, permission_id),
  created_at timestamptz DEFAULT now()
);

-- Create user_roles table (links auth.users to roles)
CREATE TABLE IF NOT EXISTS user_roles (
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  role_id uuid REFERENCES roles(role_id) ON DELETE CASCADE,
  assigned_at timestamptz DEFAULT now(),
  PRIMARY KEY (user_id, role_id)
);

-- Insert default roles
INSERT INTO roles (role_name, description) VALUES
  ('admin', 'Full control over the system with analysis access, cannot place orders'),
  ('delivery_person', 'Can report incidents and view tracking, cannot place orders'),
  ('customer', 'Basic user with order placement access')
ON CONFLICT (role_name) DO NOTHING;

-- Insert permissions
INSERT INTO permissions (permission_name, description) VALUES
  ('place_order', 'Can place new orders'),
  ('view_tracking', 'Can view shipment tracking'),
  ('access_knowledge_base', 'Can access the knowledge base'),
  ('report_incident', 'Can report incidents'),
  ('perform_analysis', 'Can perform data analysis'),
  ('access_chat', 'Can access the chat interface'),
  ('full_admin_access', 'Full administrative access to all features')
ON CONFLICT (permission_name) DO NOTHING;

-- Clear existing role-permission mappings (in case of re-run)
DELETE FROM role_permissions;

-- Assign permissions to roles
-- Admin: Can access analysis, knowledge base, tracking, chat (NO orders, NO incidents)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'admin' 
  AND p.permission_name IN ('view_tracking', 'access_knowledge_base', 'perform_analysis', 'access_chat', 'full_admin_access');

-- Delivery Person: Can report incidents, view tracking, chat (NO orders, NO analysis)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'delivery_person' 
  AND p.permission_name IN ('view_tracking', 'report_incident', 'access_chat');

-- Customer: Can place orders, view tracking, chat (NO analysis, NO incidents)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'customer' 
  AND p.permission_name IN ('place_order', 'view_tracking', 'access_chat');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);

-- ========================================
-- PART 3: RBAC FUNCTIONS
-- ========================================

-- Function to get user permissions
CREATE OR REPLACE FUNCTION get_user_permissions(user_uuid uuid)
RETURNS TABLE (permission_name text) AS $$
BEGIN
  RETURN QUERY
  SELECT DISTINCT p.permission_name
  FROM user_roles ur
  JOIN role_permissions rp ON ur.role_id = rp.role_id
  JOIN permissions p ON rp.permission_id = p.permission_id
  WHERE ur.user_id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has a specific permission
CREATE OR REPLACE FUNCTION user_has_permission(user_uuid uuid, perm_name text)
RETURNS boolean AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    JOIN permissions p ON rp.permission_id = p.permission_id
    WHERE ur.user_id = user_uuid AND p.permission_name = perm_name
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user roles
CREATE OR REPLACE FUNCTION get_user_roles(user_uuid uuid)
RETURNS TABLE (role_name text) AS $$
BEGIN
  RETURN QUERY
  SELECT r.role_name
  FROM user_roles ur
  JOIN roles r ON ur.role_id = r.role_id
  WHERE ur.user_id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- PART 4: TABLE INTEGRATION WITH RBAC
-- ========================================

-- Add user_id to customers table
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'customers' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE customers ADD COLUMN user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE;
        CREATE INDEX idx_customers_user_id ON customers(user_id);
    END IF;
END $$;

-- Add created_by to orders table
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'orders' AND column_name = 'created_by'
    ) THEN
        ALTER TABLE orders ADD COLUMN created_by uuid REFERENCES auth.users(id);
        CREATE INDEX idx_orders_created_by ON orders(created_by);
    END IF;
END $$;

-- Add reported_by to documents table
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'documents' AND column_name = 'reported_by'
    ) THEN
        ALTER TABLE documents ADD COLUMN reported_by uuid REFERENCES auth.users(id);
        CREATE INDEX idx_documents_reported_by ON documents(reported_by);
    END IF;
END $$;

-- Add user_id to agent_audit_logs
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'agent_audit_logs' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE agent_audit_logs ADD COLUMN user_id uuid REFERENCES auth.users(id);
        CREATE INDEX idx_agent_audit_logs_user_id ON agent_audit_logs(user_id);
    END IF;
END $$;

-- ========================================
-- PART 5: HELPER VIEWS AND FUNCTIONS
-- ========================================

-- Create user permissions view
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

-- Function to check if a user can perform an action
CREATE OR REPLACE FUNCTION can_user_perform_action(
    user_uuid uuid,
    action_name text
)
RETURNS boolean AS $$
BEGIN
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

-- Create audit log for role changes
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

-- Trigger to log role changes
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

-- Function to get user's full profile with role
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

-- Function to assign default customer role to new users
CREATE OR REPLACE FUNCTION assign_default_role()
RETURNS TRIGGER AS $$
BEGIN
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

-- Create materialized view for role statistics
DROP MATERIALIZED VIEW IF EXISTS role_statistics CASCADE;
CREATE MATERIALIZED VIEW role_statistics AS
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

-- Additional performance indexes
CREATE INDEX IF NOT EXISTS idx_agent_audit_logs_timestamp ON agent_audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_documents_source_type ON documents(source_type);
CREATE INDEX IF NOT EXISTS idx_documents_ts ON documents(ts DESC);

-- ========================================
-- SETUP COMPLETE!
-- ========================================

-- Verification
SELECT 'Setup Complete!' as status;
SELECT 'Tables created: ' || COUNT(*)::text as info
FROM information_schema.tables 
WHERE table_schema = 'public';

SELECT 'Roles: ' || COUNT(*)::text as info FROM roles;
SELECT 'Permissions: ' || COUNT(*)::text as info FROM permissions;
SELECT 'Role-Permission Mappings: ' || COUNT(*)::text as info FROM role_permissions;
