-- Enable the pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the customers table
CREATE TABLE customers (
  customer_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  name text,
  phone text,
  address jsonb,
  loyalty_tier text,
  created_at timestamptz DEFAULT now()
);

-- Create the orders table
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

-- Create the warehouses table
CREATE TABLE warehouses (
    warehouse_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    lat double precision,
    lon double precision,
    region text
);

-- Create the vehicles table
CREATE TABLE vehicles (
    vehicle_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_type text,
    capacity_kg numeric,
    capacity_volume_cm3 numeric,
    fuel_type text,
    status text
);

-- Create the shipments table
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

-- Create the vehicle_telemetry table (time-series data)
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

-- Create agent_audit_logs table
CREATE TABLE agent_audit_logs (
    log_id bigserial PRIMARY KEY,
    agent_name text NOT NULL,
    decision_json jsonb,
    confidence numeric,
    timestamp timestamptz DEFAULT now(),
    input_context jsonb
);

-- Create the documents table for RAG with a vector column
CREATE TABLE documents (
    doc_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type text, -- e.g., 'incident_report', 'supplier_contract'
    source_id text,
    region_id text,
    ts timestamptz,
    chunk_index integer,
    text_snippet text,
    embedding_model text,
    embedding vector(768) -- Dimension for 'nomic-embed-text'
);

-- --- INDEXES ---
CREATE INDEX idx_telemetry_vehicle_ts ON vehicle_telemetry(vehicle_id, ts DESC);
CREATE INDEX idx_shipments_status_eta ON shipments(status, current_eta);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);

-- Create an HNSW index for fast vector similarity search on the 'documents' table
CREATE INDEX idx_documents_embedding ON documents USING hnsw (embedding vector_l2_ops);


-- --- ENABLE REALTIME ---
-- This part is important for the frontend later. It allows Supabase to push updates.
-- You might need to run these commands one by one if the UI has issues with multiple statements.
begin;
  -- remove the EXCEPTION block if you are sure the publication does not exist
  create publication supabase_realtime for all tables;
exception
  when duplicate_object then
    -- publication already exists, do nothing
end;
commit;

-- Add specific tables to the publication for real-time updates
alter publication supabase_realtime add table shipments;
alter publication supabase_realtime add table vehicle_telemetry;