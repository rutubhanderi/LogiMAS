-- Enable the pg_crypto extension for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Calculate Shipping Cost
CREATE OR REPLACE FUNCTION calculate_shipping_cost(
  distance_km FLOAT,
  weight_kg FLOAT,
  packaging_type_id UUID,
  is_express BOOLEAN DEFAULT false
) RETURNS DECIMAL(10,2) AS $$
DECLARE
  base_rate DECIMAL(10,2);
  weight_charge DECIMAL(10,2);
  packaging_multiplier DECIMAL(3,2);
  express_surcharge DECIMAL(10,2) := 1.0; -- 0% by default
  total_cost DECIMAL(10,2);
BEGIN
  -- Base rate: ₹15 per km
  base_rate := 15.0 * distance_km;
  
  -- Weight charge: ₹10 per kg
  weight_charge := 10.0 * weight_kg;
  
  -- Get packaging multiplier
  SELECT multiplier INTO packaging_multiplier 
  FROM packaging_types 
  WHERE id = packaging_type_id 
  LIMIT 1;
  
  -- Set default if not found
  IF packaging_multiplier IS NULL THEN
    packaging_multiplier := 1.0;
  END IF;
  
  -- Add express surcharge if applicable
  IF is_express THEN
    express_surcharge := 1.5; -- 50% surcharge for express delivery
  END IF;
  
  -- Calculate total cost
  total_cost := (base_rate + weight_charge) * packaging_multiplier * express_surcharge;
  
  -- Ensure minimum charge
  IF total_cost < 50.0 THEN
    total_cost := 50.0;
  END IF;
  
  RETURN ROUND(total_cost, 2);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Get Shipment Status History
CREATE OR REPLACE FUNCTION get_shipment_status_history(shipment_id UUID)
RETURNS TABLE (
  status TEXT,
  status_timestamp TIMESTAMPTZ,
  location TEXT,
  notes TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    s.status::TEXT,
    s.updated_at as status_timestamp,
    COALESCE(l.name, 'Unknown') as location,
    s.notes
  FROM shipments s
  LEFT JOIN locations l ON s.location_id = l.id
  WHERE s.id = shipment_id
  ORDER BY s.updated_at DESC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- 3. Get Available Vehicles for Shipment
CREATE OR REPLACE FUNCTION get_available_vehicles(
  required_capacity FLOAT,
  required_type TEXT,
  start_time TIMESTAMPTZ,
  end_time TIMESTAMPTZ
) 
RETURNS TABLE (
  vehicle_id UUID,
  registration_number TEXT,
  capacity FLOAT,
  vehicle_type TEXT,
  current_location TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    v.id as vehicle_id,
    v.registration_number,
    v.capacity,
    v.vehicle_type,
    COALESCE(l.name, 'Depot') as current_location
  FROM vehicles v
  LEFT JOIN locations l ON v.current_location_id = l.id
  WHERE v.status = 'available'
    AND v.capacity >= required_capacity
    AND v.vehicle_type = required_type
    AND v.id NOT IN (
      SELECT vehicle_id 
      FROM shipments 
      WHERE 
        (start_time, end_time) OVERLAPS (pickup_time, delivery_estimated_time)
        AND status NOT IN ('delivered', 'cancelled')
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- 4. Get Driver Performance Metrics
CREATE OR REPLACE FUNCTION get_driver_performance(
  driver_id UUID,
  start_date DATE DEFAULT (CURRENT_DATE - INTERVAL '30 days'),
  end_date DATE DEFAULT CURRENT_DATE
)
RETURNS JSONB AS $$
DECLARE
  result JSONB;
BEGIN
  WITH stats AS (
    SELECT
      COUNT(*) as total_deliveries,
      AVG(EXTRACT(EPOCH FROM (actual_delivery_time - pickup_time)) / 3600) as avg_hours_per_delivery,
      COUNT(*) FILTER (WHERE status = 'delivered' AND actual_delivery_time <= delivery_estimated_time) as on_time_deliveries,
      COUNT(*) FILTER (WHERE status = 'delivered') as completed_deliveries,
      COUNT(*) FILTER (WHERE status = 'delayed') as delayed_deliveries,
      COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled_deliveries
    FROM shipments
    WHERE driver_id = driver_id
      AND pickup_time BETWEEN start_date AND (end_date + INTERVAL '1 day')
  )
  SELECT 
    jsonb_build_object(
      'total_deliveries', COALESCE(total_deliveries, 0),
      'on_time_rate', ROUND(COALESCE(on_time_deliveries::FLOAT / NULLIF(completed_deliveries, 0), 0) * 100, 2),
      'avg_delivery_time_hours', ROUND(COALESCE(avg_hours_per_delivery, 0), 2),
      'completion_rate', ROUND(COALESCE(completed_deliveries::FLOAT / NULLIF(total_deliveries, 0), 0) * 100, 2),
      'delayed_deliveries', COALESCE(delayed_deliveries, 0),
      'cancelled_deliveries', COALESCE(cancelled_deliveries, 0)
    )
  INTO result
  FROM stats;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- 5. Get Warehouse Inventory Summary
CREATE OR REPLACE FUNCTION get_warehouse_inventory(warehouse_id UUID)
RETURNS TABLE (
  item_id UUID,
  item_name TEXT,
  category TEXT,
  current_stock INTEGER,
  min_required_stock INTEGER,
  status TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    i.id as item_id,
    i.name as item_name,
    i.category,
    COALESCE(SUM(ii.quantity), 0) as current_stock,
    i.min_required_stock,
    CASE 
      WHEN COALESCE(SUM(ii.quantity), 0) <= 0 THEN 'Out of Stock'
      WHEN COALESCE(SUM(ii.quantity), 0) <= i.min_required_stock THEN 'Low Stock'
      ELSE 'In Stock'
    END as status
  FROM inventory_items i
  LEFT JOIN inventory ii ON i.id = ii.item_id AND ii.warehouse_id = warehouse_id
  GROUP BY i.id, i.name, i.category, i.min_required_stock
  ORDER BY status, i.name;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
