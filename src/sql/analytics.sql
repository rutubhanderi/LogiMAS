-- Create analytics_summary table
CREATE TABLE IF NOT EXISTS public.analytics_summary (
  id SERIAL PRIMARY KEY,
  total_revenue NUMERIC DEFAULT 0,
  delivery_success_rate NUMERIC DEFAULT 0,
  avg_delivery_time INTERVAL DEFAULT '0 minutes',
  customer_satisfaction NUMERIC DEFAULT 0,
  revenue_trend_json JSONB DEFAULT '{}',
  delivery_status_distribution JSONB DEFAULT '{}',
  top_delivery_personnel JSONB DEFAULT '{}',
  popular_routes JSONB DEFAULT '{}',
  last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  period VARCHAR(10) DEFAULT '30d'
);

-- Ensure at least one row exists
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM public.analytics_summary WHERE id = 1) THEN
    INSERT INTO public.analytics_summary (total_revenue, delivery_success_rate, avg_delivery_time, customer_satisfaction)
    VALUES (0, 0, '0 minutes', 0);
  END IF;
END$$;

-- Functions and triggers (the user-provided SQL for aggregations)
-- Function to calculate total revenue (last 30 days)
CREATE OR REPLACE FUNCTION calculate_total_revenue(period VARCHAR DEFAULT '30d')
RETURNS NUMERIC AS $$
BEGIN
  RETURN COALESCE((
    SELECT SUM(o.order_total)
    FROM public.orders o
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 ' || period
      AND o.status = 'delivered'
  ), 0);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate delivery success rate (last 30 days)
CREATE OR REPLACE FUNCTION calculate_delivery_success_rate(period VARCHAR DEFAULT '30d')
RETURNS NUMERIC AS $$
BEGIN
  RETURN COALESCE((
    SELECT 
      CASE 
        WHEN COUNT(*) = 0 THEN 0
        ELSE ROUND((COUNT(CASE WHEN s.status = 'delivered' THEN 1 END)::NUMERIC / COUNT(*)) * 100, 2)
      END
    FROM public.shipments s
    JOIN public.orders o ON s.order_id = o.order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 ' || period
  ), 0);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate average delivery time (last 30 days)
CREATE OR REPLACE FUNCTION calculate_avg_delivery_time(period VARCHAR DEFAULT '30d')
RETURNS INTERVAL AS $$
BEGIN
  RETURN COALESCE((
    SELECT AVG(o.actual_delivery_date - o.estimated_delivery_date)
    FROM public.orders o
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 ' || period
      AND o.status = 'delivered'
      AND o.actual_delivery_date IS NOT NULL
      AND o.estimated_delivery_date IS NOT NULL
  ), '0 minutes');
END;
$$ LANGUAGE plpgsql;

-- Function to calculate customer satisfaction (simplified as a placeholder; assumes a rating in orders)
CREATE OR REPLACE FUNCTION calculate_customer_satisfaction(period VARCHAR DEFAULT '30d')
RETURNS NUMERIC AS $$
BEGIN
  RETURN COALESCE((
    SELECT AVG((o.items->>'rating')::NUMERIC)
    FROM public.orders o
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 ' || period
      AND o.status = 'delivered'
      AND o.items->>'rating' IS NOT NULL
  ), 0);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate revenue trend (last 30 days, daily breakdown)
CREATE OR REPLACE FUNCTION calculate_revenue_trend(period VARCHAR DEFAULT '30d')
RETURNS JSONB AS $$
BEGIN
  RETURN (
    SELECT jsonb_object_agg(
      to_char(o.order_date, 'YYYY-MM-DD'),
      COALESCE(SUM(o.order_total), 0)
    )
    FROM public.orders o
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 ' || period
      AND o.status = 'delivered'
    GROUP BY to_char(o.order_date, 'YYYY-MM-DD')
  );
END;
$$ LANGUAGE plpgsql;

-- Function to calculate delivery status distribution (last 7 days)
CREATE OR REPLACE FUNCTION calculate_delivery_status_distribution(period VARCHAR DEFAULT '7d')
RETURNS JSONB AS $$
BEGIN
  RETURN (
    SELECT jsonb_object_agg(s.status, COUNT(*))
    FROM public.shipments s
    JOIN public.orders o ON s.order_id = o.order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 ' || period
    GROUP BY s.status
  );
END;
$$ LANGUAGE plpgsql;

-- Function to calculate top delivery personnel (last 30 days, based on deliveries)
CREATE OR REPLACE FUNCTION calculate_top_delivery_personnel(period VARCHAR DEFAULT '30d')
RETURNS JSONB AS $$
BEGIN
  RETURN (
    SELECT jsonb_build_object(
      'personnel',
      jsonb_agg(jsonb_build_object(
        'name', c.name,
        'deliveries', COUNT(s.shipment_id),
        'rating', COALESCE(AVG((o.items->>'rating')::NUMERIC), 0)
      ))
    )
    FROM public.shipments s
    JOIN public.orders o ON s.order_id = o.order_id
    JOIN public.customers c ON o.customer_id = c.customer_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 ' || period
      AND s.status = 'delivered'
    GROUP BY c.name
    ORDER BY COUNT(s.shipment_id) DESC
    LIMIT 3
  );
END;
$$ LANGUAGE plpgsql;

-- Function to calculate popular routes (last 30 days, based on shipments)
CREATE OR REPLACE FUNCTION calculate_popular_routes(period VARCHAR DEFAULT '30d')
RETURNS JSONB AS $$
BEGIN
  RETURN (
    SELECT jsonb_build_object(
      'routes',
      jsonb_agg(jsonb_build_object(
        'route', o.destination->>'city' || ' -> ' || w.name,
        'shipments', COUNT(s.shipment_id)
      ))
    )
    FROM public.shipments s
    JOIN public.orders o ON s.order_id = o.order_id
    JOIN public.warehouses w ON s.origin_warehouse_id = w.warehouse_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 ' || period
    GROUP BY o.destination->>'city', w.name
    ORDER BY COUNT(s.shipment_id) DESC
    LIMIT 3
  );
END;
$$ LANGUAGE plpgsql;

-- Main function to update analytics summary
CREATE OR REPLACE FUNCTION update_analytics_summary()
RETURNS VOID AS $$
BEGIN
  UPDATE public.analytics_summary
  SET
    total_revenue = calculate_total_revenue(),
    delivery_success_rate = calculate_delivery_success_rate(),
    avg_delivery_time = calculate_avg_delivery_time(),
    customer_satisfaction = calculate_customer_satisfaction(),
    revenue_trend_json = calculate_revenue_trend(),
    delivery_status_distribution = calculate_delivery_status_distribution(),
    top_delivery_personnel = calculate_top_delivery_personnel(),
    popular_routes = calculate_popular_routes(),
    last_updated = CURRENT_TIMESTAMP
  WHERE id = 1; -- Assuming single row for simplicity
END;
$$ LANGUAGE plpgsql;

-- Triggers to call updater when orders or shipments change
CREATE OR REPLACE FUNCTION trigger_update_analytics_on_orders()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM update_analytics_summary();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_analytics_after_orders ON public.orders;
CREATE TRIGGER trigger_update_analytics_after_orders
  AFTER INSERT OR UPDATE OR DELETE ON public.orders
  FOR EACH STATEMENT
  EXECUTE FUNCTION trigger_update_analytics_on_orders();

CREATE OR REPLACE FUNCTION trigger_update_analytics_on_shipments()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM update_analytics_summary();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_analytics_after_shipments ON public.shipments;
CREATE TRIGGER trigger_update_analytics_after_shipments
  AFTER INSERT OR UPDATE OR DELETE ON public.shipments
  FOR EACH STATEMENT
  EXECUTE FUNCTION trigger_update_analytics_on_shipments();
