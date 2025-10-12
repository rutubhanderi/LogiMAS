-- ========================================
-- CLEAN SETUP - Drops existing tables and recreates everything
-- Run this if you're getting UUID errors
-- ========================================

-- Drop all existing tables (in correct order)
DROP TABLE IF EXISTS shipments CASCADE;
DROP TABLE IF EXISTS vehicle_telemetry CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS vehicles CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS agent_audit_logs CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS role_change_audit CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS role_permissions CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP MATERIALIZED VIEW IF EXISTS role_statistics CASCADE;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- ========================================
-- CREATE TABLES WITH PROPER DEFAULTS
-- ========================================

-- Customers table
CREATE TABLE customers (
  customer_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  name text,
  phone text,
  address jsonb,
  loyalty_tier text,
  created_at timestamptz DEFAULT now()
);

-- Orders table
CREATE TABLE orders (
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

-- Warehouses table
CREATE TABLE warehouses (
    warehouse_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    lat double precision,
    lon double precision,
    region text
);

-- Vehicles table
CREATE TABLE vehicles (
    vehicle_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_type text,
    capacity_kg numeric,
    capacity_volume_cm3 numeric,
    fuel_type text,
    status text
);

-- Shipments table
CREATE TABLE shipments (
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

-- Vehicle telemetry table
CREATE TABLE vehicle_telemetry (
    id bigserial PRIMARY KEY,
    vehicle_id uuid REFERENCES vehicles(vehicle_id),
    ts timestamptz NOT NULL,
    lat double precision,
    lon double precision,
    speed_kmph numeric,
    fuel_pct numeric,
    cargo_temp numeric
);

-- Agent audit logs table
CREATE TABLE agent_audit_logs (
    log_id bigserial PRIMARY KEY,
    agent_name text NOT NULL,
    decision_json jsonb,
    confidence numeric,
    timestamp timestamptz DEFAULT now(),
    input_context jsonb
);

-- Documents table for RAG
CREATE TABLE documents (
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
CREATE INDEX idx_telemetry_vehicle_ts ON vehicle_telemetry(vehicle_id, ts DESC);
CREATE INDEX idx_shipments_status_eta ON shipments(status, current_eta);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_documents_embedding ON documents USING hnsw (embedding vector_l2_ops);

-- ========================================
-- RBAC TABLES
-- ========================================

CREATE TABLE roles (
  role_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  role_name text UNIQUE NOT NULL,
  description text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE permissions (
  permission_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  permission_name text UNIQUE NOT NULL,
  description text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE role_permissions (
  role_id uuid REFERENCES roles(role_id) ON DELETE CASCADE,
  permission_id uuid REFERENCES permissions(permission_id) ON DELETE CASCADE,
  PRIMARY KEY (role_id, permission_id),
  created_at timestamptz DEFAULT now()
);

CREATE TABLE user_roles (
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  role_id uuid REFERENCES roles(role_id) ON DELETE CASCADE,
  assigned_at timestamptz DEFAULT now(),
  PRIMARY KEY (user_id, role_id)
);

-- Insert roles
INSERT INTO roles (role_name, description) VALUES
  ('admin', 'Full control with analysis access'),
  ('delivery_person', 'Can report incidents and view tracking'),
  ('customer', 'Can place orders and view tracking');

-- Insert permissions
INSERT INTO permissions (permission_name, description) VALUES
  ('place_order', 'Can place new orders'),
  ('view_tracking', 'Can view shipment tracking'),
  ('access_knowledge_base', 'Can access the knowledge base'),
  ('report_incident', 'Can report incidents'),
  ('perform_analysis', 'Can perform data analysis'),
  ('access_chat', 'Can access the chat interface'),
  ('full_admin_access', 'Full administrative access');

-- Assign permissions to roles
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'admin' 
  AND p.permission_name IN ('view_tracking', 'access_knowledge_base', 'perform_analysis', 'access_chat', 'full_admin_access');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'delivery_person' 
  AND p.permission_name IN ('view_tracking', 'report_incident', 'access_chat');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'customer' 
  AND p.permission_name IN ('place_order', 'view_tracking', 'access_chat');

-- Create indexes
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);

-- ========================================
-- RBAC FUNCTIONS
-- ========================================

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
-- TABLE INTEGRATION
-- ========================================

ALTER TABLE customers ADD COLUMN user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE orders ADD COLUMN created_by uuid REFERENCES auth.users(id);
ALTER TABLE documents ADD COLUMN reported_by uuid REFERENCES auth.users(id);
ALTER TABLE agent_audit_logs ADD COLUMN user_id uuid REFERENCES auth.users(id);

CREATE INDEX idx_customers_user_id ON customers(user_id);
CREATE INDEX idx_orders_created_by ON orders(created_by);
CREATE INDEX idx_documents_reported_by ON documents(reported_by);
CREATE INDEX idx_agent_audit_logs_user_id ON agent_audit_logs(user_id);

-- ========================================
-- HELPER VIEWS
-- ========================================

CREATE VIEW user_permissions_view AS
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

-- ========================================
-- VERIFICATION
-- ========================================

SELECT 'Setup Complete!' as status;
SELECT 'Tables: ' || COUNT(*)::text FROM information_schema.tables WHERE table_schema = 'public';
SELECT 'Roles: ' || COUNT(*)::text FROM roles;
SELECT 'Permissions: ' || COUNT(*)::text FROM permissions;

-- Verify UUID defaults
SELECT 
    table_name,
    column_name,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name LIKE '%_id'
  AND column_default LIKE '%gen_random_uuid%'
ORDER BY table_name;
