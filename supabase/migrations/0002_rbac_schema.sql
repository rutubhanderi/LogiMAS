-- Role-Based Access Control (RBAC) Schema Migration
-- This migration adds tables for roles, permissions, and user role assignments

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

-- Assign permissions to roles
-- Admin: Full control with analysis, cannot place orders
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'admin' 
  AND p.permission_name IN ('view_tracking', 'access_knowledge_base', 'perform_analysis', 'access_chat', 'full_admin_access')
ON CONFLICT DO NOTHING;

-- Delivery Person: Can report incidents and view tracking, cannot place orders
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'delivery_person' 
  AND p.permission_name IN ('view_tracking', 'report_incident', 'access_chat')
ON CONFLICT DO NOTHING;

-- Customer: Basic functions (place orders only)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r, permissions p
WHERE r.role_name = 'customer' 
  AND p.permission_name IN ('place_order', 'view_tracking', 'access_chat')
ON CONFLICT DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);

-- Create a function to get user permissions
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

-- Create a function to check if user has a specific permission
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

-- Create a function to get user roles
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
-- DUMMY DATA FOR TESTING
-- ========================================

-- Insert dummy users into auth.users (if they don't exist)
-- Note: In production, users should be created through Supabase Auth signup
-- These are placeholder UUIDs for testing purposes

-- Dummy Admin User
INSERT INTO auth.users (
  id,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  raw_app_meta_data,
  raw_user_meta_data,
  is_super_admin,
  role
) VALUES (
  '11111111-1111-1111-1111-111111111111'::uuid,
  'admin@logimas.com',
  crypt('admin123', gen_salt('bf')), -- Password: admin123
  now(),
  now(),
  now(),
  '{"provider":"email","providers":["email"]}'::jsonb,
  '{"name":"Admin User"}'::jsonb,
  false,
  'authenticated'
) ON CONFLICT (id) DO NOTHING;

-- Dummy Delivery Person User
INSERT INTO auth.users (
  id,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  raw_app_meta_data,
  raw_user_meta_data,
  is_super_admin,
  role
) VALUES (
  '22222222-2222-2222-2222-222222222222'::uuid,
  'delivery@logimas.com',
  crypt('delivery123', gen_salt('bf')), -- Password: delivery123
  now(),
  now(),
  now(),
  '{"provider":"email","providers":["email"]}'::jsonb,
  '{"name":"Delivery Person"}'::jsonb,
  false,
  'authenticated'
) ON CONFLICT (id) DO NOTHING;

-- Dummy Customer User
INSERT INTO auth.users (
  id,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  raw_app_meta_data,
  raw_user_meta_data,
  is_super_admin,
  role
) VALUES (
  '33333333-3333-3333-3333-333333333333'::uuid,
  'customer@logimas.com',
  crypt('customer123', gen_salt('bf')), -- Password: customer123
  now(),
  now(),
  now(),
  '{"provider":"email","providers":["email"]}'::jsonb,
  '{"name":"Customer User"}'::jsonb,
  false,
  'authenticated'
) ON CONFLICT (id) DO NOTHING;

-- Assign Admin role to admin user
INSERT INTO user_roles (user_id, role_id)
SELECT '11111111-1111-1111-1111-111111111111'::uuid, role_id
FROM roles
WHERE role_name = 'admin'
ON CONFLICT DO NOTHING;

-- Assign Delivery Person role to delivery user
INSERT INTO user_roles (user_id, role_id)
SELECT '22222222-2222-2222-2222-222222222222'::uuid, role_id
FROM roles
WHERE role_name = 'delivery_person'
ON CONFLICT DO NOTHING;

-- Assign Customer role to customer user
INSERT INTO user_roles (user_id, role_id)
SELECT '33333333-3333-3333-3333-333333333333'::uuid, role_id
FROM roles
WHERE role_name = 'customer'
ON CONFLICT DO NOTHING;
